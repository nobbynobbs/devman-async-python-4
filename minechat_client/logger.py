import asyncio
import atexit
from datetime import datetime

from minechat_client import observer


class Logger(observer.Observer):
    """could be used insde running coroutine only
    (asyncio.get_running_loop is used)
    """
    def __init__(self, filename):
        self.filename = filename
        self._file = open(self.filename, "a")
        self._loop = asyncio.get_running_loop()
        atexit.register(self._cleanup)

    async def log(self, message):
        """согласен, открытие файла на каждый чих это дичь,
        но по-другому тоже будет дичь, правда другая
        у aiofiles довольно странный интерфейс - aiofiles.open
        возвращает контекстный менеджер, а не что-то типа
        file-like object, и с ним нельзя сделать
        ```
        aio_fd = aiofiles.open(filname, mode)
        await aio_fd.write(content)
        ``` - это не работает.

        вот это:
        ```
        aiofiles_cm = aipfiles.open(filname, mode)
        with aiofiles_cm as aio_fd:
            await aio_fd.write(content)
        ```
        работает ровно один раз, при повторной попытке
        использовать aiofiles_cm уже не работает

        соответственно единственный вариант это написать
        контекстный менеджер где-то снаружи
        и завернуть в него все приложение

        но мне это не нравится, потому что
        1. ненужная вложенность
        2. "дескриптор" нужен только логгеру, а знать о нем
        зачем-то придется всему приложению.

        поэтому решил пусть уже лучше дергает диск.

        еще один вариант - выбросить aiofiles
        """
        await self._loop.run_in_executor(
            None, self._write_log, message
        )

    async def update(self, message):
        """hardcoded formatter could be refactored"""
        await self.log(format_message(message))

    def _cleanup(self):
        self._file.close()

    def _write_log(self, message):
        """blocking io"""
        self._file.write(message)
        self._file.flush()


def format_message(message):
    """add datetime prefix to message"""
    end_of_line = ""
    if not str(message).endswith("\n"):
        end_of_line = "\n"
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return "[{}] {}{}".format(current_time, message, end_of_line)
