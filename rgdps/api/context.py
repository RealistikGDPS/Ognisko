# from __future__ import annotations # This causes a pydantic issue. Yikes.
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi import Request
from meilisearch_python_sdk import AsyncClient as MeiliClient
from redis.asyncio import Redis
from types_aiobotocore_s3 import S3Client

from rgdps.common.cache.base import AbstractAsyncCache
from rgdps.common.context import Context
from rgdps.services.boomlings import GeometryDashClient
from rgdps.services.mysql import AbstractMySQLService
from rgdps.services.storage import AbstractStorage

if TYPE_CHECKING:
    from rgdps.models.user import User


class HTTPContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def mysql(self) -> AbstractMySQLService:
        # NOTE: This is a per-request transaction.
        return self.request.state.mysql

    @property
    def redis(self) -> Redis:
        return self.request.app.state.redis

    @property
    def meili(self) -> MeiliClient:
        return self.request.app.state.meili

    @property
    def storage(self) -> AbstractStorage:
        return self.request.app.state.storage

    @property
    def user_cache(self) -> "AbstractAsyncCache[User]":
        return self.request.app.state.user_cache

    @property
    def password_cache(self) -> AbstractAsyncCache[str]:
        return self.request.app.state.password_cache

    @property
    def gd(self) -> GeometryDashClient:
        return self.request.app.state.gd


# FIXME: Proper context for pubsub handlers that does not rely on app.
class PubsubContext(Context):
    """A shared context for pubsub handlers."""

    def __init__(self, app: FastAPI) -> None:
        self.state = app.state

    @property
    def mysql(self) -> AbstractMySQLService:
        return self.state.mysql

    @property
    def redis(self) -> Redis:
        return self.state.redis

    @property
    def meili(self) -> MeiliClient:
        return self.state.meili

    @property
    def s3(self) -> S3Client | None:
        return self.state.s3

    @property
    def user_cache(self) -> "AbstractAsyncCache[User]":
        return self.state.user_cache

    @property
    def password_cache(self) -> AbstractAsyncCache[str]:
        return self.state.password_cache

    @property
    def storage(self) -> AbstractStorage:
        return self.state.storage

    @property
    def gd(self) -> GeometryDashClient:
        return self.state.gd
