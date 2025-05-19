class Config:
    DEFAULT_ADDR: str = "nats://0.0.0.0:4222"
    MANAGER_MARDUK_LOG_FILE: str = "./torchft/marduk/logging/marduk.log"
    MANAGER_RUNTIME_LOG_FILE: str = "./torchft/marduk/logging/manager.log"
    MARDUK_CONSTANTS_LOG_FILE: str = "./torchft/marduk/logging/marduk_constants.log"
    MARDUK_UTILS_LOG_FILE: str = "./torchft/marduk/logging/marduk_utils.log"
    MARDUK_CONTROLLER_LOG_FILE: str = "./torchft/marduk/logging/marduk_controller.log"
    MARDUK_MONITOR_CLI_LOG_FILE: str = "./torchft/marduk/logging/marduk_monitor_cli.log"
    FORMAT_LOG: bool = False
    NC_TIMEOUT: float = 1
    EXCEPTION_RETRY_TIME: float = 1
    CONNECTION_RETRY_TIME: float = 1