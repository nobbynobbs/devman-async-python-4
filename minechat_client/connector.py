import asyncio
import socket

import minechat_client.observer as observer


async def _exponential_backoff(backoff=0.1, max_delay=5):
    """calculate and yield delay duration"""
    attempt = 0
    while True:
        delay = backoff * (2 ** attempt)
        if delay > max_delay:
            """prevent redundant calculations"""
            break
        attempt += 1
        yield delay
    while True:
        yield max_delay


class MinechatConnection(observer.Observable):

    def __init__(self, host, port, subscribers=None, timeout=1):
        self.host = host
        self.port = port
        self.reader, self.writer = None, None
        self.timeout = timeout
        super().__init__(subscribers)

    async def __aenter__(self):
        async for delay in _exponential_backoff():
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    self.timeout
                )
            except (
                ConnectionRefusedError, ConnectionResetError, socket.gaierror
            ):
                await self.notify(
                    "Connection error, retry after {:.2f} seconds".format(
                        delay
                    )
                )
                await asyncio.sleep(delay)
            else:
                await self.notify("Connection established")
                return self.reader, self.writer

    async def __aexit__(self, exc, exc_type, trace):
        self.writer.close()
        await self.writer.wait_closed()
