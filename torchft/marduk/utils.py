from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUUID
import torch
def get_device_uuid():
    nvmlInit()
    index = torch.cuda.current_device()
    handle = nvmlDeviceGetHandleByIndex(index)

    gpu_uuid = nvmlDeviceGetUUID(handle)
    return gpu_uuid