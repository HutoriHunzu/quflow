from collections import deque

from .base import StorageBase, T


class SingleItemStorage(StorageBase[T]):
    def __init__(self):
        self.maxsize = 1
        self.deque = deque(maxlen=self.maxsize)

    def write(self, data: T | None = None):
        if data is not None:
            self.deque.append(data)

    def read(self) -> T | None:
        try:
            return self.deque.pop()
        except IndexError:
            return None

    def __len__(self) -> int:
        return len(self.deque)

    @property
    def type(self):
        return 'SingleItemStorage'


    def is_empty(self) -> bool:
        return not bool(self) # bool on deque returns if it has anything
