from __future__ import annotations

from abc import ABC
from abc import abstractmethod

__all__ = (
    "AbstractAsyncCache",
    "AbstractCache",
    "KeyType",
)

type KeyType = str | int


class AbstractCache[T](ABC):
    @abstractmethod
    def get(self, key: KeyType) -> T | None: ...

    @abstractmethod
    def set(self, key: KeyType, value: T) -> None: ...

    @abstractmethod
    def delete(self, key: KeyType) -> None: ...


class AbstractAsyncCache[T](ABC):
    @abstractmethod
    async def get(self, key: KeyType) -> T | None: ...

    @abstractmethod
    async def set(self, key: KeyType, value: T) -> None: ...

    @abstractmethod
    async def delete(self, key: KeyType) -> None: ...
