from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUUID
def get_device_id():

    # Initialize NVML
    nvmlInit()

    # Get the handle for GPU index 0 (change index as needed)
    handle = nvmlDeviceGetHandleByIndex(0)

    # Query its UUID
    gpu_uuid = nvmlDeviceGetUUID(handle)
    print("GPU 0 UUID:", gpu_uuid)
    return gpu_uuid

get_device_id()
