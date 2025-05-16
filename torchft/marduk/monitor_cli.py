import argparse
import asyncio
import cmd

import nats
from torchft.marduk.marduk_pb2 import EventEnvelope
import time
from torchft.marduk.constants import MardukConstants, MonitorStream, ControllerStream

class MyShell(cmd.Cmd):
    prompt = 'marduk> '
    intro = "Marduk CLI"

    def __init__(self, completekey = "tab", stdin = None, stdout = None):
        super().__init__(completekey, stdin, stdout)
        self.loop = asyncio.get_event_loop()

    def do_test(self, line):
        self.loop.run_until_complete(self._send_device_err(line))

    async def _send_device_err(self, line):
        print(f"Failed GPU uuid: {line}")
        nc =  await nats.connect(MardukConstants.DEFAULT_ADDR)
        # await js.add_stream(name=MardukConstants.controller_stream.STREAM, subjects=[MardukConstants.monitor_stream.subjects.EXTERNAL])
        DRenvelope = EventEnvelope()
        DRenvelope.monitored_fail.device_uuid = line
        
        await nc.publish(MardukConstants.monitor_stream.subjects.EXTERNAL, DRenvelope.SerializeToString())

    def do_quit(self, line):
        return True

    def default(self, line):
        print(f"Unknown cmd: {line}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Marduk CLI")
    parser.add_argument("--host", type=str, default="localhost", help="NATS server host")
    parser.add_argument("--port", type=int, default=4222, help="NATS server port")
    args = parser.parse_args()

    shell = MyShell()
    if args.host and args.port:
        MardukConstants.DEFAULT_ADDR = f"nats://{args.host}:{args.port}"
        
    MyShell().cmdloop()