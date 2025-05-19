import time
from datetime import timedelta
from unittest import TestCase
from unittest.mock import create_autospec

import torch.distributed as dist

from torchft.manager import Manager
from torchft.process_group import ProcessGroup
from torchft._torchft import LighthouseServer


class FailureNotificationTest(TestCase):
    def _start_manager(self, lighthouse_addr: str, replica_id: str, port: int):
        store = dist.TCPStore(
            host_name="localhost", port=0, is_master=True, wait_for_workers=False
        )
        pg = create_autospec(ProcessGroup)
        pg.abort.return_value = None
        manager = Manager(
            pg=pg,
            min_replica_size=2,
            load_state_dict=lambda x: None,
            state_dict=lambda: None,
            replica_id=replica_id,
            store_addr="localhost",
            store_port=store.port,
            rank=0,
            world_size=1,
            lighthouse_addr=lighthouse_addr,
            port=port,
            heartbeat_interval=timedelta(milliseconds=50),
            use_async_quorum=False,
        )
        return manager, pg

    def _measure(self, timeout_ms: int) -> float:
        lighthouse = LighthouseServer(
            bind="[::]:0", min_replicas=2, heartbeat_timeout_ms=timeout_ms
        )
        try:
            m1, pg1 = self._start_manager(lighthouse.address(), "rep1", 19531)
            m2, _ = self._start_manager(lighthouse.address(), "rep2", 19532)
            # allow heartbeats to register
            time.sleep(0.2)
            m2.shutdown(wait=False)

            start = time.perf_counter()
            while pg1.abort.call_count == 0:
                if time.perf_counter() - start > 5:
                    break
                time.sleep(0.05)
            elapsed = time.perf_counter() - start
            m1.shutdown(wait=False)
            return elapsed
        finally:
            lighthouse.shutdown()

    def test_failure_detection_fast(self) -> None:
        elapsed = self._measure(timeout_ms=200)
        self.assertLess(elapsed, 1.0)

    def test_failure_detection_slow(self) -> None:
        elapsed = self._measure(timeout_ms=1000)
        self.assertGreater(elapsed, 1.0)
