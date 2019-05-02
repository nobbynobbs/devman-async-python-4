import abc

"""
Я видел в описании к заданиям, что не надо делать сложно
и изобретать абстракции, но без этой штуки "логировать"
в файлик несвязанные процессы установления соединения
и чтения из сокета было очень неудобно и некрасиво.
"""

class Observable(abc.ABC):
    def __init__(self, subscribers=None):
        if subscribers is None:
            subscribers = []
        self.subscribers = subscribers

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        try:
            self.subscribers.remove(subscriber)
        except ValueError:
            pass  # ignore exception

    async def notify(self, message):
        """notify subscribers"""
        for subscriber in self.subscribers:
            await subscriber.update(message)


class Observer(abc.ABC):
    """something like Observer"""

    @abc.abstractmethod
    async def handle_update(self, message):
        pass

    async def update(self, message):
        await self.handle_update(message)
