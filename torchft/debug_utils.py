class DebugLog:
    def __init__(self, prefix: str=''):
        self.log_file = "debug.log"
        self.prefix = prefix
    def write(self, msg: str) -> None:
        with open(self.log_file, "a") as f:
            f.write(f"{self.prefix}: {msg}\n")

def write_debug_log(msg: str, prefix: str='') -> None:
    """
    Helper function to write a message to debug.log.
    """
    with open("debug.log", "a") as f:
        f.write(f"{prefix}: {msg}\n")

dl_manager = DebugLog("manager")
dl_lighthouse = DebugLog("lighthouse")
dl_lighthouse_client = DebugLog("lighthouse_client")
dl_failure_listener = DebugLog("failure_listener")
dl_manager_client = DebugLog("manager_client")
dl_train = DebugLog("train")