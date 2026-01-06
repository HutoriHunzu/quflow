from abc import abstractmethod
from typing import Generic, TypeVar
from ..storage import StorageBase, SingleItemStorage, MultiItemStorage

T = TypeVar('T')
W = TypeVar('W')

# Define interfaces for read and write strategies.
class WriteStrategy(Generic[T, W]):

    @abstractmethod
    def write(self, storage: StorageBase[T], data: W | None = None) -> None:
        pass

    @abstractmethod
    def validate(self, storage: StorageBase[T]):
        pass


class SingleWriteStrategy(WriteStrategy[T, T]):

    def write(self, storage: SingleItemStorage[T] | MultiItemStorage[T], data: T | None = None) -> None:
        return storage.write(data)

    def validate(self, storage: SingleItemStorage[T] | MultiItemStorage[T]):
        if not (isinstance(storage, SingleItemStorage) or isinstance(storage, MultiItemStorage)):
            raise TypeError(f'SingleWriteStrategy doesnt works with {type(storage)}')


class MultiWriteStrategy(WriteStrategy[T, list[T]]):

    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size

    def write(self, storage: MultiItemStorage[T], data: list[T] | None = None) -> None:
        if data is None:
            return
        for elem in data:
            storage.write(elem)

    def validate(self, storage: StorageBase[T]):
        if not isinstance(storage, MultiItemStorage):
            raise TypeError(f'MultiWriteStrategy doesnt works with {type(storage)}')
