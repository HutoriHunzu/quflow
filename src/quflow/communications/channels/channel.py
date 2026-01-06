import threading
from typing import Generic, TypeVar, Callable, List
from ..storage import StorageBase
from .read_strategy import ReadStrategy
from .write_strategy import WriteStrategy

T = TypeVar('T')
R = TypeVar('R')
W = TypeVar('W')


class Channel(Generic[T, R, W]):
    """A unidirectional data pipe from one Node to another.

    Stores data in a StorageBase (either SingleItemStorage or MultiItemStorage),
    and uses read/write strategies to determine how data is consumed and produced.

    Args:
        storage (StorageBase[T]): The underlying storage type (e.g., queue or single slot).
        read_strategy (ReadStrategy[T, R]): Defines how reading occurs (single or multi).
        write_strategy (WriteStrategy[T, W]): Defines how writing occurs (single or multi).

    Methods:
        read() -> R: Reads data from the channel, returning None if no data.
        write(data: W): Writes data to the channel, ignoring None if not present.
        is_empty() -> bool: True if the storage has no data left.

    Example:
        chan = Channel(
            storage=SingleItemStorage(),
            read_strategy=SingleReadStrategy(),
            write_strategy=SingleWriteStrategy()
        )
    """

    def __init__(
            self,
            storage: StorageBase[T],
            read_strategy: ReadStrategy[T, R],
            write_strategy: WriteStrategy[T, W],
    ):
        self.storage = storage
        self.read_strategy = read_strategy
        self.write_strategy = write_strategy
        self.validate()

    def read(self) -> R | None:
        return self.read_strategy.read(self.storage)

    def write(self, data: W | None = None) -> None:
        self.write_strategy.write(self.storage, data)

    def is_empty(self) -> bool:
        return self.storage.is_empty()

    def validate(self):
        self.read_strategy.validate(self.storage)
        self.write_strategy.validate(self.storage)
