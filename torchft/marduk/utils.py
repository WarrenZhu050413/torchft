import asyncio
from typing import Tuple, Any, Dict
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUUID
import torch
from torchft.marduk.logging.log_utils import log_and_raise_exception
from torchft.marduk.logging.logger import logger

def get_device_uuid():
    try:
        nvmlInit()
        index = torch.cuda.current_device()
        handle = nvmlDeviceGetHandleByIndex(index)
        gpu_uuid = nvmlDeviceGetUUID(handle)
        logger.info(f"Retrieved GPU UUID: {gpu_uuid} for device index {index}")
        return gpu_uuid
    except Exception as e:
        log_and_raise_exception(logger, f"Failed to get device UUID: {e}", exc_info=True)

async def cancel_subscriptions(subscriptions: Dict[str, Tuple[Any, asyncio.Task]]):
    # cancel all the tasks
    for (_, task) in subscriptions.values():
        task.cancel()

    # wait for cancellation to finish
    await asyncio.gather(
        *(task for _, task in subscriptions.values()),
        return_exceptions=True
    )

    # unsubscribe from NATS
    for (sub, _) in subscriptions.values():
        await sub.unsubscribe()