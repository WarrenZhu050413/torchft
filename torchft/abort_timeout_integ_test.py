import multiprocessing
import time
from datetime import timedelta
from unittest import TestCase

import torch
import torch.distributed as dist

from torchft._torchft import LighthouseServer
from torchft.manager import Manager
from torchft.process_group import ProcessGroupGloo


def _worker(rank: int, store_port: int, lighthouse_addr: str, q: multiprocessing.Queue) -> None:
    pg = ProcessGroupGloo()
    manager = Manager(
        pg=pg,
        min_replica_size=2,
        load_state_dict=lambda x: None,
        state_dict=lambda: None,
        replica_id=str(rank),
        store_addr="localhost",
        store_port=store_port,
        rank=rank,
        world_size=2,
        lighthouse_addr=lighthouse_addr,
        port=19530 + rank,
        timeout=timedelta(minutes=2),
        use_async_quorum=False,
    )
    try:
        manager.start_quorum()
        while True:
            t = torch.ones(1)
            fut = manager.allreduce(t)
            fut.wait()
            time.sleep(1)
    except Exception:
        q.put(time.time())
    finally:
        manager.shutdown(wait=False)


class AbortTimeoutIntegTest(TestCase):
    def test_abort_timeout(self) -> None:
        lighthouse = LighthouseServer(bind="[::]:0", min_replicas=2)
        store = dist.TCPStore(
            host_name="localhost",
            port=0,
            is_master=True,
            wait_for_workers=False,
        )

        ctx = multiprocessing.get_context("spawn")
        q: multiprocessing.Queue[float] = ctx.Queue()
        p0 = ctx.Process(target=_worker, args=(0, store.port, lighthouse.address(), q))
        p1 = ctx.Process(target=_worker, args=(1, store.port, lighthouse.address(), q))
        p0.start()
        p1.start()

        time.sleep(2)
        kill_time = time.time()
        p0.kill()

        abort_time = q.get(timeout=180)
        duration = abort_time - kill_time

        lighthouse.shutdown()
        p1.join(timeout=10)
        p0.join(timeout=10)

        self.assertLess(duration, 150)

