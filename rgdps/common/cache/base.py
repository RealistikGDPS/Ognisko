from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

__all__ = (
    "AbstractAsyncCache",
    "AbstractCache",
    "KeyType",
)

T = TypeVar("T")
KeyType = str | int


class AbstractCache(ABC, Generic[T]):
    @abstractmethod
    def get(self, key: KeyType) -> T | None:
        ...

    @abstractmethod
    def set(self, key: KeyType, value: T) -> None:
        ...

    @abstractmethod
    def delete(self, key: KeyType) -> None:
        ...


class AbstractAsyncCache(ABC, Generic[T]):
    @abstractmethod
    async def get(self, key: KeyType) -> T | None:
        ...

    @abstractmethod
    async def set(self, key: KeyType, value: T) -> None:
        ...

    @abstractmethod
    async def delete(self, key: KeyType) -> None:
        ...
