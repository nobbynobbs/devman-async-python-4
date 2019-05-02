from datetime import datetime

import aiofiles

from minechat_client import observer


class Logger(observer.Observer):

    def __init__(self, filename):
        self.filename = filename

    async def log(self, message):
        async with aiofiles.open(self.filename, "a") as aio_fd:
            await aio_fd.write(message)
            await aio_fd.flush()

    async def handle_update(self, message):
        """hardcoded formatter could be refactored"""
        await self.log(format_message(message))


def format_message(message):
    """add datetime prefix to message"""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    end_of_line = ""
    if not message.endswith("\n"):
        end_of_line = "\n"
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return "[{}] {}{}".format(current_time, message, end_of_line)
