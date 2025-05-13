from dataclasses import dataclass

class MardukSubjects:
    EXTERNAL: str = "marduk.monitored.failure"
    CONTROLLER_EVENTS: str = "marduk.controller.events"
    DR_SUBJECT: str = "marduk.DRentry"

class ControllerSubjects:
    DR_SUBJECT: str = MardukSubjects.DR_SUBJECT

class ControllerStream:
    STREAM: str = "CONTROLLER-STREAM"
    CONTROLLER_CONSUMER: str = "controller-consumer"
    subjects = ControllerSubjects()

class MonitorSubjects:
    EXTERNAL: str = MardukSubjects.EXTERNAL
    CONTROLLER_EVENTS: str = MardukSubjects.CONTROLLER_EVENTS

class MonitorStream:
    STREAM: str = "MONITOR-STREAM"
    CONSUMER: str = "monitor-consumer"
    subjects = MonitorSubjects()

@dataclass
class MardukConstants:
    """Constants for Marduk communication channels and configuration."""
    subjects: MardukSubjects = MardukSubjects()
    controller_stream: ControllerStream = ControllerStream()
    monitor_stream: MonitorStream = MonitorStream()
    DEFAULT_ADDR: str = "nats://0.0.0.0:4222"