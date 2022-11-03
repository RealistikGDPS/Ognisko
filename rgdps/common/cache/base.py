from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union

__all__ = (
    "AsyncCacheBase",
    "CacheBase",
    "KeyType",
)

T = TypeVar("T")
KeyType = Union[str, int]


class CacheBase(ABC, Generic[T]):
    @abstractmethod
    def get(self, key: KeyType) -> Optional[T]:
        ...

    @abstractmethod
    def set(self, key: KeyType, value: T) -> None:
        ...

    @abstractmethod
    def delete(self, key: KeyType) -> None:
        ...


class AsyncCacheBase(ABC, Generic[T]):
    @abstractmethod
    async def get(self, key: KeyType) -> Optional[T]:
        ...

    @abstractmethod
    async def set(self, key: KeyType, value: T) -> None:
        ...

    @abstractmethod
    async def delete(self, key: KeyType) -> None:
        ...
