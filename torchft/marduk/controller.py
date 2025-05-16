import threading, queue, nats, asyncio, os, signal, _thread
import time

from typing import List, Dict, Callable, Awaitable, Set

from nats.aio.client import Client
import nats.errors
from nats.aio.msg import Msg
from nats.js.client import JetStreamContext
from torchft.marduk.marduk_pb2 import EventEnvelope, DeviceReplicaMapEntry
from torchft.marduk.constants import MardukConstants

class Controller():
    """Controller for Zeus training.

    This class is responsible for managing the training process, including
    handling events and managing resources. It runs in a separate thread to
    avoid blocking the main thread.

    It is the sole producer.
    """

    def __init__(self, marduk_addr: str = MardukConstants.DEFAULT_ADDR):
        self._stop = threading.Event()
        # Many-to-many mapping between devices and replicas
        self.device_to_replicas: Dict[str, Set[str]] = {}  # device_uuid -> set of replica_ids
        self.replica_to_devices: Dict[str, Set[str]] = {}  # replica_id -> set of device_uuids
        self._nc: Client | None = None
        self._js: JetStreamContext | None = None
        self.seq = 0
        self._marduk_addr = marduk_addr
        self._loop = asyncio.get_event_loop()
        self._subscriptions = {}
        self._nc_timeout = 1
        self._exception_sleep = 1

    async def marduk_connect(self):
        try:
            self._nc = await nats.connect(self._marduk_addr)
            self._js = self._nc.jetstream()
            print("Connected to NATS server")
        except Exception as e:
            print(f"Failed to connect to NATS server: {e}")
            raise
        
    async def message_handler(self, msg):
        try:
            env = EventEnvelope()
            env.ParseFromString(msg.data)
            # Handle different event types
            if env.HasField("register_device"):
                await self.message_handler_register_device(env)
            
            if env.HasField("monitored_fail"):
                await self.message_handler_handle_gpu_failure(env)
                
        except Exception as e:
            print(f"Error handling message: {e}")

    async def message_handler_register_device(self, env: EventEnvelope):
        device_uuid = env.register_device.device_uuid
        replica_id = env.register_device.replica_id
        
        # Update device to replicas mapping
        if device_uuid not in self.device_to_replicas:
            self.device_to_replicas[device_uuid] = set()
        
        is_new_device_association = replica_id not in self.device_to_replicas[device_uuid]
        if is_new_device_association:
            self.device_to_replicas[device_uuid].add(replica_id)
            print(f"New Mapping: Device {device_uuid} is now associated with replicas: {self.device_to_replicas[device_uuid]}")
        
        # Update replica to devices mapping
        if replica_id not in self.replica_to_devices:
            self.replica_to_devices[replica_id] = set()
        
        is_new_replica_association = device_uuid not in self.replica_to_devices[replica_id]
        if is_new_replica_association:
            self.replica_to_devices[replica_id].add(device_uuid)
            print(f"New Mapping: Replica {replica_id} is now associated with devices: {self.replica_to_devices[replica_id]}")

    async def message_handler_handle_gpu_failure(self, env: EventEnvelope):
        try:
            fail_event = env.monitored_fail
            device_uuid = fail_event.device_uuid
            print(f"[GPU FAILURE] Device: {device_uuid}")
            
            if device_uuid in self.device_to_replicas:
                replica_ids = self.device_to_replicas[device_uuid]
                print(f"[GPU FAILURE] Associated Replica IDs: {replica_ids}")
                
                # Handle failure - you might want to notify all replicas associated with this device
                for replica_id in replica_ids:
                    print(f"[GPU FAILURE] Notifying replica: {replica_id}")
                    # Add logic to handle notification here
            else:
                print(f"[GPU FAILURE] Device not found in device-to-replicas map")
        except Exception as e:
            print(f"Error handling GPU failure message: {str(e)}")

    # Helper methods to query the mapping
    def get_replicas_for_device(self, device_uuid: str) -> Set[str]:
        """Get all replicas associated with a device."""
        return self.device_to_replicas.get(device_uuid, set())
    
    def get_devices_for_replica(self, replica_id: str) -> Set[str]:
        """Get all devices associated with a replica."""
        return self.replica_to_devices.get(replica_id, set())
    
    def remove_device_replica_association(self, device_uuid: str, replica_id: str) -> bool:
        """Remove an association between a device and a replica. Returns True if association existed."""
        success = False
        
        if device_uuid in self.device_to_replicas and replica_id in self.device_to_replicas[device_uuid]:
            self.device_to_replicas[device_uuid].remove(replica_id)
            success = True
            if not self.device_to_replicas[device_uuid]:  # Clean up empty sets
                del self.device_to_replicas[device_uuid]
        
        if replica_id in self.replica_to_devices and device_uuid in self.replica_to_devices[replica_id]:
            self.replica_to_devices[replica_id].remove(device_uuid)
            success = True
            if not self.replica_to_devices[replica_id]:  # Clean up empty sets
                del self.replica_to_devices[replica_id]
        
        return success

    async def maybe_add_stream(self, stream: str, subjects: List[str]|str):
        if self._js is None:
            await self.marduk_connect()
            assert self._js is not None

        try:
            await self._js.stream_info(stream)
        except nats.errors.Error:
            target_subjects = subjects if isinstance(subjects, list) else [subjects]
            await self._js.add_stream(name=stream, subjects=target_subjects)

    async def subscribe_js(self, stream: str, subject: str, consumer: str, message_handler: Callable[[Msg], Awaitable[None]]):
        if not self._js:
            await self.marduk_connect()
            assert self._js is not None


        await self.maybe_add_stream(stream, subject)
        print(f"Subscribing to {subject} on stream {stream} with consumer {consumer}")

        psub = await self._js.pull_subscribe(subject, durable=consumer, stream=stream)

        async def listen_to_js_subscription():
            while True:
                try:
                    # fetch(1) will wait up to 1 second if no messages are available
                    msgs = await psub.fetch(1, timeout=1)
                except TimeoutError:
                    # no new messages this cycle; loop and try again
                    continue

                await asyncio.gather(
                    *[message_handler(msg) for msg in msgs]
                )

                await asyncio.gather(
                    *[msg.ack() for msg in msgs]
                )

        task = asyncio.create_task(listen_to_js_subscription())
        self._subscriptions[subject] = (psub, task)

    async def subscribe_nc(self, subject: str, message_handler: Callable[[Msg], Awaitable[None]]) -> None:
        if not self._nc:
            print("Connecting to NATS server")
            await self.marduk_connect()
            assert self._nc is not None

        sub = await self._nc.subscribe(subject)
        print(f"Subscribed to {subject}")
        async def listen_to_nc_subscription():
            print("Listening to NATS subscription")
            while self._stop.is_set() is False:
                try:
                    msg = await sub.next_msg(timeout=self._nc_timeout)
                    print("Received message")
                    await message_handler(msg)
                except TimeoutError:
                    continue
                except Exception as e:
                    print(f"Error in subscription loop for {subject}: {str(e)}")
                    await asyncio.sleep(self._exception_sleep)
        
        task = asyncio.create_task(listen_to_nc_subscription())
        self._subscriptions[subject] = (sub, task)

    async def stop(self):
        # signal all loops to exit
        self._stop.set()

        # cancel all the tasks
        for (_, task) in self._subscriptions.values():
            task.cancel()

        # wait for cancellation to finish
        await asyncio.gather(
            *(task for _, task in self._subscriptions.values()),
            return_exceptions=True
        )

        # unsubscribe from NATS
        for (sub, _) in self._subscriptions.values():
            await sub.unsubscribe()

        self._subscriptions.clear()

        # finally, close connection
        if self._nc and not self._nc.is_closed:
            await self._nc.close()

async def main():
    try:
        controller = Controller()

        await controller.subscribe_js(
            MardukConstants.controller_stream.STREAM,
            MardukConstants.controller_stream.subjects.DR_SUBJECT,
            MardukConstants.controller_stream.CONSUMER,
            controller.message_handler
        )
        await controller.subscribe_nc(subject=MardukConstants.monitor_stream.subjects.EXTERNAL, 
                                     message_handler=controller.message_handler)

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Controller stopped by user")
    finally:
        await controller.stop()

if __name__ == '__main__':
    asyncio.run(main())