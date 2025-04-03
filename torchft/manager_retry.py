# retry_manager.py
from torchft.manager import Manager  # or from .manager import Manager if it's a package
import torch
from torch.distributed import ReduceOp
from typing import List

class RetryManager(Manager):
    def __init__(self, *args, collective_retry_num: int = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self.collective_retry_num = collective_retry_num

    def allreduce(
        self,
        tensor: torch.Tensor,
    ) -> torch.futures.Future[torch.Tensor]:
        """
        Like Manager.allreduce, but retries up to `collective_retry_num` times on failure.
        """

        if self.errored():
            fut = torch.futures.Future()
            fut.set_result(tensor)
            return fut

        self.wait_quorum()

        if not self.is_participating():
            tensor.zero_()

        retry_count = 0
        while retry_count < self.collective_retry_num:
            try:
                # Attempt the allreduce
                work = self._pg.allreduce([tensor], ReduceOp.SUM)
                fut = work.get_future()

                def callback(fut: torch.futures.Future[List[torch.Tensor]]) -> torch.Tensor:
                    nonlocal tensor

                    # check for exceptions
                    fut.value()

                    tensor /= self.num_participants()
                    return tensor

                # Attach callback and wrap as usual
                fut = fut.then(callback)
                fut = self.wrap_future(fut, tensor)
                return fut

            except Exception as e:
                self._logger.exception(
                    f"allreduce attempt {retry_count + 1} of {self.collective_retry_num} failed: {e}, retrying..."
                )
                retry_count += 1
                if retry_count >= self.collective_retry_num:
                    # If out of retries, report the error and return a completed Future
                    self.report_error(e)
                    fut = torch.futures.Future()
                    fut.set_result(tensor)
                    return fut