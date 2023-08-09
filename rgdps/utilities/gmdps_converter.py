# The database converter for the GMDPS database.
# Please see the README for more information.
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote

import httpx
from databases import DatabaseURL
from meilisearch_python_async import Client as MeiliClient
from redis.asyncio import Redis
from types_aiobotocore_s3 import S3Client

from rgdps import logger
from rgdps.common.cache.memory import SimpleAsyncMemoryCache
from rgdps.common.context import Context
from rgdps.config import config

if TYPE_CHECKING:
    from rgdps.models.user import User
    from rgdps.common.cache.base import AbstractAsyncCache
    from rgdps.services.mysql import MySQLService


@dataclass
class ConverterContext(Context):
    _mysql: MySQLService
    _redis: Redis
    _meili: MeiliClient
    _user_cache: AbstractAsyncCache[User]
    _password_cache: AbstractAsyncCache[str]
    _http: httpx.AsyncClient
    old_sql: MySQLService

    @property
    def mysql(self) -> MySQLService:
        return self._mysql

    @property
    def redis(self) -> Redis:
        return self._redis

    @property
    def meili(self) -> MeiliClient:
        return self._meili

    @property
    def s3(self) -> S3Client | None:
        # We are not using storage.
        return None

    @property
    def user_cache(self) -> AbstractAsyncCache[User]:
        return self._user_cache

    @property
    def password_cache(self) -> AbstractAsyncCache[str]:
        return self._password_cache

    @property
    def http(self) -> httpx.AsyncClient:
        return self._http


async def get_context() -> ConverterContext:
    database_url = DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=config.sql_user,
            password=quote(config.sql_pass),
            host=config.sql_host,
            port=config.sql_port,
            db=config.sql_db,
        ),
    )

    mysql = MySQLService(database_url)
    await mysql.connect()

    old_database_url = DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=config.sql_user,
            password=quote(config.sql_pass),
            host=config.sql_host,
            port=config.sql_port,
            db=config.sql_db,
        ),
    )

    old_sql = MySQLService(old_database_url)
    await old_sql.connect()

    redis = Redis.from_url(
        f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    )
    await redis.initialize()

    meili = MeiliClient(
        f"http://{config.meili_host}:{config.meili_port}",
        config.meili_key,
        timeout=10,
    )
    await meili.health()

    user_cache = SimpleAsyncMemoryCache[User]()
    password_cache = SimpleAsyncMemoryCache[str]()
    http = httpx.AsyncClient()

    return ConverterContext(
        mysql,
        redis,
        meili,
        user_cache,
        password_cache,
        http,
        old_sql,
    )


async def main() -> int:
    logger.info("Starting the GMDPS -> RealistikGDPS converter.")
    context = await get_context()

    logger.info("Successfully connected!")
    return 0
