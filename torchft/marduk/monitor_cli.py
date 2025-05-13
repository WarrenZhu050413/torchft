import asyncio
import cmd

import nats
from torchft.marduk.marduk_pb2 import EventEnvelope

from torchft.marduk.constants import MardukConstants, MonitorStream

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
        js = nc.jetstream()
        DRenvelope = EventEnvelope()
        DRenvelope.monitored_fail.device_uuid = line

        await js.publish(MardukConstants.subjects.EXTERNAL, DRenvelope.SerializeToString())


    def do_quit(self, line):
        return True

    def default(self, line):
        print(f"Unknown cmd: {line}")

if __name__ == '__main__':
    MyShell().cmdloop()