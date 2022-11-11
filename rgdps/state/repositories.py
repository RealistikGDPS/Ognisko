from __future__ import annotations

from redis.asyncio import Redis

from rgdps.common.cache.base import AbstractAsyncCache
from rgdps.common.cache.memory import SimpleAsyncMemoryCache
from rgdps.common.cache.redis import SimpleRedisCache
from rgdps.models.user import User

user_repo: AbstractAsyncCache[User]
password_cache: AbstractAsyncCache[str]


def setup_stateful() -> None:
    global user_repo
    global password_cache

    user_repo = SimpleAsyncMemoryCache()
    password_cache = SimpleAsyncMemoryCache()


# This needing to take redis implies we have a design issue.
def setup_stateless(redis: Redis) -> None:
    global user_repo
    global password_cache

    user_repo = SimpleRedisCache(
        redis=redis,
        key_prefix="rgdps:cache:user",
    )
    password_cache = SimpleRedisCache(
        redis=redis,
        key_prefix="rgdps:cache:password",
        deserialise=lambda x: x.decode(),
        serialise=lambda x: x.encode(),
    )
