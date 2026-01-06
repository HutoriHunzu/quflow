from queue import Queue, Empty
from .base import StorageBase, T


class MultiItemStorage(StorageBase[T]):

    def __init__(self, maxsize: int = 0):
        self.maxsize = maxsize
        self.queue = Queue(maxsize=maxsize)

    def write(self, data: T | None = None):
        if data is not None:
            self.queue.put_nowait(data)

    def read(self) -> T | None:
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def __len__(self) -> int:
        return self.queue.qsize()

    @property
    def type(self):
        return 'MultiItemStorage'

    def is_empty(self) -> bool:
        return self.queue.empty()
