from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from meilisearch_python_sdk import AsyncClient as MeiliClient
from redis.asyncio import Redis

from rgdps.adapters import AbstractMySQLService
from rgdps.adapters import AbstractStorage
from rgdps.adapters import GeometryDashClient
from rgdps.common.cache import AbstractAsyncCache

from .save_data import SaveData
from .save_data import SaveDataRepository

from .user import User
from .user import UserRepository

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
    def password_cache(self) -> AbstractAsyncCache[str]: ...

    @property
    @abstractmethod
    def gd(self) -> GeometryDashClient: ...
