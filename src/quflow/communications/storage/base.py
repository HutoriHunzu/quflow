from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from enum import StrEnum, auto


T = TypeVar("T")


class StorageNames(StrEnum):
    MULTI_ITEM = auto()
    SINGLE_ITEM = auto()


class StorageBase(ABC, Generic[T]):
    @abstractmethod
    def write(self, data: T):
        pass

    @abstractmethod
    def read(self) -> T | None:
        """
        Note that the reading on an
        empty storage shouldn't raise errors
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @property
    @abstractmethod
    def type(self) -> StorageNames:
        pass
