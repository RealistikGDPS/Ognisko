from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

import httpx
from meilisearch_python_sdk import AsyncClient as MeiliClient
from redis.asyncio import Redis
from types_aiobotocore_s3 import S3Client

if TYPE_CHECKING:
    from rgdps.models.user import User
    from rgdps.common.cache.base import AbstractAsyncCache
    from rgdps.services.mysql import AbstractMySQLService
    from rgdps.services.storage import AbstractStorage


class Context(ABC):
    @property
    @abstractmethod
    def mysql(self) -> AbstractMySQLService: ...

    @property
    @abstractmethod
    def redis(self) -> Redis: ...

    @property
    @abstractmethod
    def meili(self) -> MeiliClient: ...

    @property
    @abstractmethod
    def storage(self) -> AbstractStorage: ...

    @property
    @abstractmethod
    def user_cache(self) -> AbstractAsyncCache[User]: ...

    @property
    @abstractmethod
    def password_cache(self) -> AbstractAsyncCache[str]: ...

    @property
    @abstractmethod
    def http(self) -> httpx.AsyncClient: ...
