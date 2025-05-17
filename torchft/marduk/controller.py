import nats, asyncio

from typing import Dict, Callable, Awaitable, Set

from nats.aio.client import Client
import nats.errors
from nats.aio.msg import Msg
from nats.js.client import JetStreamContext
from torchft.marduk.config import Config
from torchft.marduk.marduk_pb2 import EventEnvelope, MonitoredFailEvent
from torchft.marduk.constants import MardukConstants, NC, JS
from torchft.marduk.logging.logger import logger
from torchft.marduk.logging.log_utils import log_and_raise_exception
from torchft.marduk.utils import cancel_subscriptions

class Controller():
    """Controller for Marduk.

    This class is responsible for managing the training process, including
    handling events and managing resources. It runs in a separate thread to
    avoid blocking the main thread.

    It is the sole producer of events.
    """

    def __init__(self, marduk_addr: str = MardukConstants.DEFAULT_ADDR) -> None:
        self._stop_nats = asyncio.Event()
        # Many-to-many mapping between devices and replicas
        self.device_to_replicas: Dict[str, Set[str]] = {}  # device_uuid -> set of replica_ids
        self.replica_to_devices: Dict[str, Set[str]] = {}  # replica_id -> set of device_uuids
        self.seq = 0
        self._marduk_addr: str = marduk_addr
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._subscriptions = {}
        self._nc_timeout = Config.NC_TIMEOUT or 1   
        self._exception_sleep = Config.EXCEPTION_SLEEP or 1
        logger.info(f"Controller initialized with NATS address: {marduk_addr}")

        self._nc: Client | None = None
        self._js: JetStreamContext | None = None

    async def initialize(self) -> None:
        """Initialize NATS connection and JetStream."""
        self._nc = await nats.connect(self._marduk_addr)
        self._js = self._nc.jetstream()
        logger.info(f"Connected to NATS server at {self._marduk_addr}")

    async def message_handler(self, msg: Msg) -> None:
        try:
            env = EventEnvelope()
            env.ParseFromString(msg.data)
            logger.debug(f"Received message: {env}")
            
            # Handle different event types
            if env.HasField("register_device"):
                await self.message_handler_register_device(env)
            
            if env.HasField("monitored_fail"):
                await self.message_handler_handle_gpu_failure(env)
                
        except Exception as e:
            logger.exception(f"Error handling message: {e}")

    async def message_handler_register_device(self, env: EventEnvelope):
        device_uuid: str = env.register_device.device_uuid
        replica_id: str = env.register_device.replica_id

        logger.info("\n" + "-" * 100)
        logger.info(f"Received register_device event for device {device_uuid} and replica {replica_id}")
        
        # Update device to replicas mapping
        if device_uuid not in self.device_to_replicas:
            self.device_to_replicas[device_uuid] = set()
        
        is_new_device_association = replica_id not in self.device_to_replicas[device_uuid]
        if is_new_device_association:
            self.device_to_replicas[device_uuid].add(replica_id)
            logger.info(f"New Mapping: Device {device_uuid} is now associated with replicas: {self.device_to_replicas[device_uuid]}")
        
        # Update replica to devices mapping
        if replica_id not in self.replica_to_devices:
            self.replica_to_devices[replica_id] = set()
        
        is_new_replica_association = device_uuid not in self.replica_to_devices[replica_id]
        if is_new_replica_association:
            self.replica_to_devices[replica_id].add(device_uuid)
            logger.info(f"New Mapping: Replica {replica_id} is now associated with devices: {self.replica_to_devices[replica_id]}")

    async def message_handler_handle_gpu_failure(self, env: EventEnvelope):
        try:
            fail_event: MonitoredFailEvent = env.monitored_fail
            device_uuid: str = fail_event.device_uuid
            if device_uuid in self.device_to_replicas:
                replica_ids: Set[str] = self.get_replicas_for_device(device_uuid)
                logger.info(f"[GPU FAILURE] Associated Replica IDs: {replica_ids}")
                
                for replica_id in replica_ids:
                    await self.send_replica_fail_event(replica_id)
            else:
                logger.warning(f"[GPU FAILURE] Device {device_uuid} not found in device-to-replicas map")
        except Exception as e:
            logger.exception(f"Error handling GPU failure message: {e}")

    async def send_replica_fail_event(self, replica_id: str) -> None:
        self.maybe_log_and_raise_exception(NC)
        assert self._nc is not None # This should always be true because we check it in maybe_log_and_raise_exception

        env: EventEnvelope = EventEnvelope()
        env.replica_fail.replica_id = replica_id
        await self._nc.publish(MardukConstants.subjects.REPLICA_FAIL, env.SerializeToString())

    def get_replicas_for_device(self, device_uuid: str) -> Set[str]:
        return self.device_to_replicas.get(device_uuid, set())
    
    def get_devices_for_replica(self, replica_id: str) -> Set[str]:
        return self.replica_to_devices.get(replica_id, set())
    
    async def subscribe_js(self, stream: str, subject: str, consumer: str, message_handler: Callable[[Msg], Awaitable[None]]) -> None:
        self.maybe_log_and_raise_exception(JS)
        assert self._js is not None

        logger.info(f"Subscribing to {subject} on stream {stream} with consumer {consumer}")

        psub = await self._js.pull_subscribe(subject, durable=consumer, stream=stream)

        async def listen_to_js_subscription():
            logger.info(f"Started listening on {subject}")
            while True:
                try:
                    # fetch(1) will wait up to 1 second if no messages are available
                    msgs = await psub.fetch(1, timeout=1)
                    logger.debug(f"Received {len(msgs)} messages on {subject}")
                except TimeoutError:
                    # no new messages this cycle; loop and try again
                    continue
                except Exception as e:
                    logger.exception(f"Error fetching messages from {subject}: {e}")
                    continue

                try:
                    await asyncio.gather(
                        *[message_handler(msg) for msg in msgs]
                    )

                    await asyncio.gather(
                        *[msg.ack() for msg in msgs]
                    )
                except Exception as e:
                    logger.exception(f"Error processing messages from {subject}: {e}")

        task = asyncio.create_task(listen_to_js_subscription())
        self._subscriptions[subject] = (psub, task)

    async def subscribe_nc(self, subject: str, message_handler: Callable[[Msg], Awaitable[None]]) -> None:
        self.maybe_log_and_raise_exception(NC)
        assert self._nc is not None # This should always be true because we check it in maybe_log_and_raise_exception

        sub = await self._nc.subscribe(subject)
        logger.info(f"Subscribed to {subject}")
        
        async def listen_to_nc_subscription():
            logger.info(f"Started listening on {subject}")
            while self._stop_nats.is_set() is False:
                try:
                    msg = await sub.next_msg(timeout=self._nc_timeout)
                    logger.debug(f"Received message on {subject}")
                    await message_handler(msg)
                except TimeoutError:
                    continue
                except Exception as e:
                    logger.exception(f"Error in subscription loop for {subject}: {e}")
                    await asyncio.sleep(self._exception_sleep)
        
        task = asyncio.create_task(listen_to_nc_subscription())
        self._subscriptions[subject] = (sub, task)

    async def stop(self):
        logger.info("Stopping Controller")
        # signal all loops to exit
        self._stop_nats.set()

        await cancel_subscriptions(self._subscriptions)
        self._subscriptions.clear()
        logger.info("All subscriptions cleared")

        # finally, close connection
        if self._nc and not self._nc.is_closed:
            await self._nc.close()
            logger.info("NATS connection closed")

    def maybe_log_and_raise_exception(self, type: str) -> None:
        if type == NC:
            if self._nc is None:
                log_and_raise_exception(logger, "NATS connection is not initialized, call initialize() first")
        elif type == JS:
            if self._js is None:
                log_and_raise_exception(logger, "JetStream is not initialized, call initialize() first")
        else:
            log_and_raise_exception(logger, f"Invalid type: {type}")

async def main():
    try:
        logger.info("Starting Marduk Controller")
        controller = Controller()
        await controller.initialize()

        await controller.subscribe_js(
            MardukConstants.controller_stream.STREAM,
            MardukConstants.controller_stream.subjects.DR_SUBJECT,
            MardukConstants.controller_stream.CONSUMER,
            controller.message_handler
        )
        await controller.subscribe_nc(subject=MardukConstants.monitor_stream.subjects.EXTERNAL, 
                                     message_handler=controller.message_handler)

        logger.info("Controller initialized and subscribed to all subjects")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Controller stopped by user")
    except Exception as e:
        logger.exception(f"Unexpected error in controller: {e}")
    finally:
        await controller.stop()

if __name__ == '__main__':
    asyncio.run(main())