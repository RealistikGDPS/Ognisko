# from __future__ import annotations # This causes a pydantic issue. Yikes.
from typing import TYPE_CHECKING

import httpx
from fastapi import Request
from meilisearch_python_async import Client as MeiliClient
from redis.asyncio import Redis

from rgdps.common.cache.base import AbstractAsyncCache
from rgdps.common.context import Context
from rgdps.services.mysql import MySQLService

if TYPE_CHECKING:
    from rgdps.models.user import User


class HTTPContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def mysql(self) -> MySQLService:
        return self.request.app.state.mysql

    @property
    def redis(self) -> Redis:
        return self.request.app.state.redis

    @property
    def meili(self) -> MeiliClient:
        return self.request.app.state.meili

    @property
    def user_cache(self) -> "AbstractAsyncCache[User]":
        return self.request.app.state.user_cache

    @property
    def password_cache(self) -> AbstractAsyncCache[str]:
        return self.request.app.state.password_cache

    @property
    def http(self) -> httpx.AsyncClient:
        return self.request.app.state.http
