import argparse
import asyncio
import cmd

import nats
from torchft.marduk.marduk_pb2 import EventEnvelope
import time
from torchft.marduk.constants import MardukConstants, MonitorStream, ControllerStream
from torchft.marduk.logging.logger import logger

class MyShell(cmd.Cmd):
    prompt = 'marduk> '
    intro = "Marduk CLI"

    def __init__(self, completekey = "tab", stdin = None, stdout = None):
        super().__init__(completekey, stdin, stdout)
        self._loop = asyncio.get_event_loop()
        logger.info("Marduk CLI initialized")
        self._nc = None

    def do_test(self, line):
        logger.info(f"Executing test command with input: {line}")
        self._loop.run_until_complete(self._send_device_err(line))

    async def _send_device_err(self, line):
        logger.info(f"Simulating failed GPU with uuid: {line}")
        try:
            if self._nc is None:
                self._nc = await nats.connect(MardukConstants.DEFAULT_ADDR)
            logger.debug(f"Connected to NATS server at {MardukConstants.DEFAULT_ADDR}")
            
            # await js.add_stream(name=MardukConstants.controller_stream.STREAM, subjects=[MardukConstants.monitor_stream.subjects.EXTERNAL])
            DRenvelope = EventEnvelope()
            DRenvelope.monitored_fail.device_uuid = line
            
            await self._nc.publish(MardukConstants.monitor_stream.subjects.EXTERNAL, DRenvelope.SerializeToString())
            logger.info(f"Published device failure event for device {line}")

        except Exception as e:
            logger.exception(f"Failed to send device error: {e}")

    def do_quit(self, line):
        logger.info("Exiting Marduk CLI")
        if self._nc is not None:
            self._loop.run_until_complete(self._nc.close())
        logger.info("NATS connection closed")
        return True

    def default(self, line):
        logger.warning(f"Unknown command: {line}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Marduk CLI")
    parser.add_argument("--host", type=str, default="localhost", help="NATS server host")
    parser.add_argument("--port", type=int, default=4222, help="NATS server port")
    args = parser.parse_args()

    if args.host and args.port:
        MardukConstants.DEFAULT_ADDR = f"nats://{args.host}:{args.port}"
        logger.info(f"Using NATS server at {MardukConstants.DEFAULT_ADDR}")
    
    logger.info("Starting Marduk CLI")
    MyShell().cmdloop()