from dataclasses import dataclass
from torchft.marduk.logging.logger import logger
from torchft.marduk.config import Config

NC = "nc"
JS = "js"

class MardukSubjects:
    EXTERNAL: str = "marduk.monitored.failure"
    CONTROLLER_EVENTS: str = "marduk.controller.events"
    DR_SUBJECT: str = "marduk.DRentry"
    REPLICA_FAIL: str = "marduk.replica.fail"

class ControllerSubjects:
    DR_SUBJECT: str = MardukSubjects.DR_SUBJECT

class StreamSpec:
    STREAM = None
    CONSUMER = None
    subjects = None

class ControllerStream(StreamSpec):
    STREAM: str = "CONTROLLER-STREAM"
    CONSUMER: str = "controller-consumer"
    subjects = ControllerSubjects()

class MonitorSubjects:
    EXTERNAL: str = MardukSubjects.EXTERNAL
    CONTROLLER_EVENTS: str = MardukSubjects.CONTROLLER_EVENTS

class MonitorStream(StreamSpec):
    STREAM: str = "MONITOR-STREAM"
    CONSUMER: str = "monitor-consumer"
    subjects = MonitorSubjects()

@dataclass
class MardukConstants:
    """Constants for Marduk communication channels and configuration."""
    subjects: MardukSubjects = MardukSubjects()
    controller_stream: ControllerStream = ControllerStream()
    monitor_stream: MonitorStream = MonitorStream()
    DEFAULT_ADDR: str = Config.DEFAULT_ADDR
    
    def __post_init__(self):
        logger.debug(f"MardukConstants initialized with DEFAULT_ADDR: {self.DEFAULT_ADDR}")
        logger.debug(f"Controller stream: {self.controller_stream.STREAM}, Consumer: {self.controller_stream.CONSUMER}")
        logger.debug(f"Monitor stream: {self.monitor_stream.STREAM}, Consumer: {self.monitor_stream.CONSUMER}")
        logger.debug(f"Subject paths: DR_SUBJECT={self.subjects.DR_SUBJECT}, EXTERNAL={self.subjects.EXTERNAL}")

# Log important constants on module import
logger.info("Marduk constants module loaded")