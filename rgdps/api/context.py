# from __future__ import annotations # This causes a pydantic issue. Yikes.
from typing import TYPE_CHECKING

import httpx
from fastapi import FastAPI
from fastapi import Request
from meilisearch_python_async import Client as MeiliClient
from redis.asyncio import Redis
from types_aiobotocore_s3 import S3Client

from rgdps.common.cache.base import AbstractAsyncCache
from rgdps.common.context import Context
from rgdps.services.mysql import MySQLService

if TYPE_CHECKING:
    from rgdps.models.user import User


class HTTPContext(Context):
    def __init__(self, request: Request) -> None:
        self.state = request.app.state

    @property
    def mysql(self) -> MySQLService:
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
    def http(self) -> httpx.AsyncClient:
        return self.state.http


class PubsubContext(HTTPContext):
    """A shared context for pubsub handlers."""

    def __init__(self, app: FastAPI) -> None:
        self.state = app.state
