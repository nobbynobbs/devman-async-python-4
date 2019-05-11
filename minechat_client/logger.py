from datetime import datetime

from minechat_client import observer


class Logger(observer.Observer):
    """could be used insde running coroutine only
    (asyncio.get_running_loop is used)
    """
    def __init__(self, async_fd):
        self.async_fd = async_fd

    async def log(self, message):
        await self.async_fd.write(message)
        await self.async_fd.flush()

    async def update(self, message):
        """hardcoded formatter could be refactored"""
        await self.log(format_message(message))


def format_message(message):
    """add datetime prefix to message"""
    end_of_line = ""
    if not str(message).endswith("\n"):
        end_of_line = "\n"
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return "[{}] {}{}".format(current_time, message, end_of_line)
