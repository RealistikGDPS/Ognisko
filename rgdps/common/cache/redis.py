from __future__ import annotations

import pickle
from typing import Callable
from typing import Optional
from typing import Type
from typing import TypeVar

from realistikgdps.state import services

from .base import AsyncCacheBase
from .base import KeyType


T = TypeVar("T")
DESERIALISE_FUNCTION = Callable[[bytes], T]
SERIALISE_FUNCTION = Callable[[T], bytes]

# Cast functions for common occurrences
# TODO: Maybe move these into a separate file?
def serialise_object(obj: object) -> bytes:
    """Indiscriminately serialises an object to bytes."""
    return pickle.dumps(obj)


def deserialise_object(data: bytes) -> object:
    """Indiscriminately deserialises bytes to an object."""
    return pickle.loads(data)


class SimpleRedisCache(AsyncCacheBase[T]):
    __slots__ = (
        "_key_prefix",
        "_deserialise",
        "_serialise",
    )

    def __init__(
        self,
        key_prefix: str,
        deserialise: DESERIALISE_FUNCTION = deserialise_object,
        serialise: SERIALISE_FUNCTION = serialise_object,
    ) -> None:
        self._key_prefix = key_prefix
        self._deserialise = deserialise
        self._serialise = serialise

    def __create_key(self, key: KeyType) -> str:
        return f"{self._key_prefix}:{key}"

    async def set(self, key: KeyType, value: T) -> None:
        await services.redis.set(self.__create_key(key), self._serialise(value))

    async def get(self, key: KeyType) -> Optional[T]:
        data = await services.redis.get(self.__create_key(key))
        if data is None:
            return None
        return self._deserialise(data)

    async def delete(self, key: KeyType) -> None:
        await services.redis.delete(self.__create_key(key))
