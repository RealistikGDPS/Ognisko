from __future__ import annotations

from typing import Optional
from typing import TypeVar

from .base import AsyncCacheBase
from .base import CacheBase
from .base import KeyType

__all__ = (
    "SimpleMemoryCache",
    "LRUMemoryCache",
    "SimpleAsyncMemoryCache",
    "LRUAsyncMemoryCache",
)

T = TypeVar("T")


def _ensure_key_type(key: KeyType) -> str:
    """To ensure behaviour parity with the database based caches, we convert
    the key to a string. This is because in memory, a key of `1` and `"1"` are
    different, but in the database, they are the same."""
    return str(key)


class SimpleMemoryCache(CacheBase[T]):
    __slots__ = ("_cache",)

    def __init__(self) -> None:
        self._cache: dict[str, T] = {}

    def get(self, key: KeyType) -> Optional[T]:
        return self._cache.get(_ensure_key_type(key))

    def set(self, key: KeyType, value: T) -> None:
        self._cache[_ensure_key_type(key)] = value

    def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass


class LRUMemoryCache(CacheBase[T]):
    __slots__ = ("_cache", "_max_size")

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._cache: dict[str, T] = {}

    def get(self, key: KeyType) -> Optional[T]:
        key_str = _ensure_key_type(key)
        value = self._cache.get(key_str)
        if value is not None:
            del self._cache[key_str]
            self._cache[key_str] = value
        return value

    def set(self, key: KeyType, value: T) -> None:
        while len(self._cache) >= self._capacity:
            # Cursed but the most efficient approach for large datasets
            del self._cache[next(iter(self._cache))]

        self._cache[_ensure_key_type(key)] = value

    def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass


# Async variants
class SimpleAsyncMemoryCache(AsyncCacheBase[T]):
    __slots__ = ("_cache",)

    def __init__(self) -> None:
        self._cache: dict[str, T] = {}

    async def get(self, key: KeyType) -> Optional[T]:
        return self._cache.get(_ensure_key_type(key))

    async def set(self, key: KeyType, value: T) -> None:
        self._cache[_ensure_key_type(key)] = value

    async def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass


class LRUAsyncMemoryCache(AsyncCacheBase[T]):
    __slots__ = ("_cache", "_max_size")

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._cache: dict[str, T] = {}

    async def get(self, key: KeyType) -> Optional[T]:
        key_str = _ensure_key_type(key)
        value = self._cache.get(key_str)
        if value is not None:
            del self._cache[key_str]
            self._cache[key_str] = value
        return value

    async def set(self, key: KeyType, value: T) -> None:
        while len(self._cache) >= self._capacity:
            # Cursed but the most efficient approach for large datasets
            del self._cache[next(iter(self._cache))]

        self._cache[_ensure_key_type(key)] = value

    async def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass
