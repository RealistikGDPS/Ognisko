from __future__ import annotations

import pickle
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from redis.asyncio import Redis

from .base import AbstractAsyncCache
from .base import KeyType


# Cast functions for common occurrences
# TODO: Maybe move these into a separate file?
def serialise_object(obj: Any) -> bytes:
    """Indiscriminately serialises an object to bytes."""
    return pickle.dumps(obj)


def deserialise_object(data: bytes) -> Any:
    """Indiscriminately deserialises bytes to an object."""
    return pickle.loads(data)


type DeserialisableFunction[T] = Callable[[bytes], T]
type SerialisableFunction[T] = Callable[[T], bytes]


class SimpleRedisCache[T](AbstractAsyncCache[T]):
    __slots__ = (
        "_key_prefix",
        "_deserialise",
        "_serialise",
        "_redis",
        "_expiry",
    )

    def __init__(
        self,
        redis: Redis,
        key_prefix: str,
        deserialise: DeserialisableFunction = deserialise_object,
        serialise: SerialisableFunction = serialise_object,
        expiry: timedelta = timedelta(days=1),
    ) -> None:
        self._key_prefix = key_prefix
        self._deserialise = deserialise
        self._serialise = serialise
        self._redis = redis
        self._expiry = expiry

    def __create_key(self, key: KeyType) -> str:
        return f"{self._key_prefix}:{key}"

    async def set(self, key: KeyType, value: T) -> None:
        await self._redis.set(
            name=self.__create_key(key),
            value=self._serialise(value),
            ex=self._expiry,
        )

    async def get(self, key: KeyType) -> T | None:
        data = await self._redis.get(self.__create_key(key))
        if data is None:
            return None
        return self._deserialise(data)

    async def delete(self, key: KeyType) -> None:
        await self._redis.delete(self.__create_key(key))
