import threading, queue, nats, asyncio, os, signal, _thread
import time

from typing import List, Dict

import nats.errors
from torchft.marduk.marduk_pb2 import EventEnvelope, DeviceReplicaMapEntry
from torchft.marduk.constants import MardukConstants, ControllerStream

# Thread‑safe FIFO for non‑fatal events
ev_queue: queue.Queue[EventEnvelope] = queue.Queue(maxsize=1024)


class Controller():
    """Controller for Zeus training.

    This class is responsible for managing the training process, including
    handling events and managing resources. It runs in a separate thread to
    avoid blocking the main thread.

    It is the sole producer.
    """

    def __init__(self, marduk_addr: str = MardukConstants.DEFAULT_ADDR):
        self.stop_evt = threading.Event()
        self.dr_map: Dict[str, int] = {}  # device_uuid -> replica_rank
        self._nc = None
        self.seq = 0
        self.marduk_addr = marduk_addr
        self._loop = asyncio.get_event_loop()

    async def handle_drmap_msg(self, msg):
        try:
            data = DeviceReplicaMapEntry().ParseFromString(msg.data)
            print(f"Received device replica map entry: {data}")
            device_uuid = data.device_uuid
            replica_id = data.replica_id
            self.dr_map[device_uuid] = replica_id
            print(f"Updated device replica map: {device_uuid} -> {replica_id}")
        except Exception as e:
            print(f"Error processing device replica map message: {e}")
        
    async def message_handler(self, msg):
        try:
            env = EventEnvelope()
            env.ParseFromString(msg.data)
            
            # Handle different event types
            if env.HasField("register_device"):
                device_uuid = env.register_device.device_uuid
                replica_id = env.register_device.replica_id
                self.dr_map[device_uuid] = replica_id
                print(f"Registered device {device_uuid} for rank {replica_id}")
                
            elif env.HasField("drain"):
                device_uuid = env.drain.device_uuid
                if device_uuid in self.dr_map:
                    print(f"Drain event for device {device_uuid}")
                    # Handle drain logic
                
            elif env.HasField("replica_fail"):
                print(f"Replica fail event for rank {env.replica_fail.replica_rank}")
                # Handle replica fail logic
                
            elif env.HasField("monitored_fail"):
                device_uuid = env.monitored_fail.device_uuid
                if device_uuid in self.dr_map:
                    print(f"Monitored fail event for device {device_uuid}")
                    # Get the replica rank associated with the failed device
                    replica_rank = self.dr_map.get(device_uuid)
                    if replica_rank is not None:
                        # Create and publish a ReplicaFailEvent
                        fail_event = EventEnvelope()
                        fail_event.seq = self.seq
                        self.seq += 1
                        fail_event.ts_nanos = time.time() * 1e9  # Current time in nanoseconds
                        fail_event.replica_fail.replica_rank = replica_rank
                        
                        # Broadcast the ReplicaFailEvent to all subscribers
                        try:
                            await self._nc.publish("marduk.controller.events.fast", fail_event.SerializeToString())
                            print(f"Broadcasted ReplicaFailEvent for rank {replica_rank}")
                        except Exception as e:
                            print(f"Failed to broadcast ReplicaFailEvent: {e}")
                    # Handle monitored fail logic
                
            elif env.HasField("change_batch_sz"):
                new_batch_size = env.change_batch_sz.new_batch_sz
                print(f"Changing batch size to {new_batch_size}")
                # Handle batch size change logic
                
            # Queue non-fatal events for processing in main thread
            try:
                ev_queue.put_nowait(env)
            except queue.Full:
                print("[WARN] event queue full; dropping message")
                
        except Exception as e:
            print(f"Error handling message: {e}")
        
    async def start(self):
        await self.connect()
        # self._loop.
        await self.listen_worker_events()

    async def connect(self):
        try:
            self._nc = await nats.connect(self.marduk_addr)
            self.js = self._nc.jetstream()
            print("Connected to NATS server")
        except Exception as e:
            print(f"Failed to connect to NATS server: {e}")
            raise

    async def add_subscription(self, stream_name: str, subject: str, consumer_name: str, message_handler: callable):
        
        sub = await self.js.pull_subscribe(subject, durable=ControllerStream.CONTROLLER_CONSUMER, stream=stream_name)
        self.subscriptions[subject] = {
            "subscription": sub,
            "stream_name": stream_name,
            "consumer_name": consumer_name,
            "message_handler": message_handler,
            "task": None
        }
        print(f"Subscribed to {subject} on stream {stream_name}")

    async def start_subscriptions(self):
        for subject, sub_info in self.subscriptions.items():
            task = asyncio.create_task(self.listen_to_subscription(subject))
            sub_info["task"] = task
            print(f"Started listening to {subject}")

    async def listen_to_subscription(self, subject):
        sub_info = self.subscriptions[subject]
        
        while self.stop_evt.is_set() is False:
            try:
                msgs = await sub_info["subscription"].fetch(1, 1)
                
                for msg in msgs:
                    await sub_info["message_handler"](msg)
                    
            except TimeoutError:
                continue
            except Exception as e:
                print(f"Error in subscription loop for {subject}: {str(e)}")
                await asyncio.sleep(1)

    async def listen_worker_events(self):
        self._nc = await nats.connect(self.marduk_addr)
        js = self._nc.jetstream()
        try:
            await js.stream_info(ControllerStream.STREAM)
        except nats.errors.Error:
            await js.add_stream(name=ControllerStream.STREAM, subjects=[ControllerStream.subjects.DR_SUBJECT])

        psub = await js.pull_subscribe(ControllerStream.subjects.DR_SUBJECT, durable=ControllerStream.CONTROLLER_CONSUMER)

        print("Controller: waiting for messages...")
        while True:
            try:
                # fetch(1) will wait up to 1 second if no messages are available
                msgs = await psub.fetch(1, timeout=1)
            except TimeoutError:
                # no new messages this cycle; loop and try again
                continue

            await asyncio.gather(
                *[self.message_handler(msg) for msg in msgs]
            )

            await asyncio.gather(
                *[msg.ack() for msg in msgs]
            )
            
    async def handle_gpu_failure(msg):
        try:
            envelope = EventEnvelope()
            envelope.ParseFromString(msg.data)
            
            if envelope.HasField('monitored_fail_event'):
                fail_event = envelope.monitored_fail_event
                print(f"[GPU FAILURE] Device: {fail_event.device_uuid}, Reason: {fail_event.reason}")
                
            await msg.ack()
        except Exception as e:
            print(f"Error handling GPU failure message: {str(e)}")
            await msg.nack()

    async def stop(self):
        self.stop_evt.set()
        
        for subject, sub_info in self.subscriptions.items():
            if sub_info["task"]:
                sub_info["task"].cancel()
                try:
                    await sub_info["task"]
                except asyncio.CancelledError:
                    pass
                print(f"Subscription loop stopped for subject: {subject}")
                
            if sub_info["subscription"]:
                await sub_info["subscription"].unsubscribe()
                
        self.subscriptions.clear()
        
        if self.nc and not self.nc.is_closed:
            await self.nc.close()
            self.nc = None
            print("NATS connection closed")

async def main():
    try:
        controller = Controller()
        await controller.add_subscription(
            ControllerStream.STREAM,
            ControllerStream.subjects.DR_SUBJECT,
            ControllerStream.CONTROLLER_CONSUMER,
            controller.message_handler
        )

        await controller.add_subscription(
            ControllerStream.STREAM,
            ControllerStream.subjects.EXTERNAL,
            ControllerStream.CONTROLLER_CONSUMER,
            controller.handle_gpu_failure
        )
        await controller.start_subscriptions()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Controller stopped by user")
    finally:
        controller.stop()

if __name__ == '__main__':
    asyncio.run(main())