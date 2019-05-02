import asyncio

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


def main(args):
    try:
        asyncio.run(run_main_loop(args))
    except KeyboardInterrupt:
        print("Good bye")
