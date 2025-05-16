class Config:
    DEFAULT_ADDR: str = "nats://0.0.0.0:4222"
    LOG_FILE: str = "/srv/apps/warren/torchft/torchft/marduk/logging/marduk.log"
    FORMAT_LOG: bool = False
    NC_TIMEOUT: float = 1
    EXCEPTION_SLEEP: float = 1