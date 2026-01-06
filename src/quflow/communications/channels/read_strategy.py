from abc import abstractmethod
from typing import Generic, TypeVar
from ..storage import StorageBase, SingleItemStorage, MultiItemStorage

T = TypeVar('T')
R_co = TypeVar('R_co', covariant=True)



# Define interfaces for read and write strategies.
class ReadStrategy(Generic[T, R_co]):

    @abstractmethod
    def read(self, storage: StorageBase) -> R_co:
        pass

    @abstractmethod
    def validate(self, storage):
        pass


class SingleReadStrategy(ReadStrategy[T, T | None]):

    def read(self, storage: SingleItemStorage[T] | MultiItemStorage[T]) -> T | None:
        return storage.read()

    def validate(self, storage: SingleItemStorage[T] | MultiItemStorage[T]):
        if not (isinstance(storage, SingleItemStorage) or isinstance(storage, MultiItemStorage)):
            raise TypeError(f'SingleReadStrategy doesnt works with {type(storage)}')


class MultiReadStrategy(ReadStrategy[T, list[T]]):

    def __init__(self, chunk_size: int | None):
        self.chunk_size = chunk_size

    def read(self, storage: MultiItemStorage[T]) -> list[T]:
        if self.chunk_size is None:
            amount_to_read = len(storage)
        else:
            amount_to_read = min(self.chunk_size, len(storage))

        read_items_generator = self.generate_read(amount_to_read, storage)

        # filter None
        return list(filter(lambda x: x is not None, read_items_generator))

    def validate(self, storage: MultiItemStorage[T]):
        if not isinstance(storage, MultiItemStorage):
            raise TypeError(f'MultiReadStrategy doesnt works with {type(storage)}')

    @staticmethod
    def generate_read(amount, storage):
        for _ in range(amount):
            yield storage.read()
