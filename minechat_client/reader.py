import asyncio
import os

import minechat_client.connector as connector
import minechat_client.observer as observer
import minechat_client.logger as logger


class Reader(observer.Observable):

    def __init__(self, reader, timeout=5, subscribers=None):
        self.reader = reader
        self.timeout = timeout
        super().__init__(subscribers)

    async def read_forever(self):
        while True:
            # Это нужный таймаут. Если у нас закончится интернет
            # или сервер на другой стороне внезапно взорвется,
            # мы будем вечно пытаться вычитать этот сокет и никак
            # не узнаем, что читать больше неоткуда.
            # Вопрос только в величине этого таймаута.
            chat_message = (
                await asyncio.wait_for(self.reader.readline(), self.timeout)
            ).decode("utf-8")
            await self.notify(chat_message)


async def run_main_loop(args):
    logger_observer = logger.Logger(args.history)
    connection = connector.MinechatConnection(
        args.host, args.port, subscribers=[logger_observer]
    )
    while True:
        async with connection as (stream_reader, _):
            reader = Reader(stream_reader, subscribers=[logger_observer])
            try:
                await reader.read_forever()
            except asyncio.TimeoutError:
                await logger_observer.log(
                    "Timeout while reading message, reconnecting"
                )
            except ConnectionResetError:
                await logger_observer.log(
                    "Connection is lost, reconnecting"
                )


def check_permissions(path):
    """check if file or containing directory is writable"""
    if os.path.exists(path):
        return os.access(path, os.W_OK)
    return os.access(
        os.path.abspath(os.path.dirname(path)), os.W_OK
    )


def main(args):
    if not check_permissions(args.history):
        print("Check if history file is writable")
        return
    try:
        asyncio.run(run_main_loop(args))
    except KeyboardInterrupt:
        print("Good bye")
