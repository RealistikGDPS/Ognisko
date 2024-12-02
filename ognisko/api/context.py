# from __future__ import annotations # This causes a pydantic issue. Yikes.

from typing import override

from fastapi import FastAPI
from fastapi import Request

from ognisko.adapters.boomlings import GeometryDashClient
from ognisko.adapters.meilisearch import MeiliSearchClient
from ognisko.adapters.mysql import ImplementsQueryableConnection
from ognisko.adapters.redis import RedisClient
from ognisko.adapters.storage import AbstractStorage
from ognisko.resources import Context


class HTTPContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    @override
    def _mysql(self) -> ImplementsQueryableConnection:
        return self.request.app.state.mysql

    @property
    @override
    def _redis(self) -> RedisClient:
        return self.request.app.state.redis

    @property
    @override
    def _meili(self) -> MeiliSearchClient:
        return self.request.app.state.meili

    @property
    @override
    def _storage(self) -> AbstractStorage:
        return self.request.app.state.storage

    @property
    @override
    def _gd(self) -> GeometryDashClient:
        return self.request.app.state.gd


# FIXME: Proper context for pubsub handlers that does not rely on app.
class PubsubContext(Context):
    """A shared context for pubsub handlers."""

    def __init__(self, app: FastAPI) -> None:
        self.state = app.state

    @property
    @override
    def _mysql(self) -> ImplementsQueryableConnection:
        return self.state.mysql

    @property
    @override
    def _redis(self) -> RedisClient:
        return self.state.redis

    @property
    @override
    def _meili(self) -> MeiliSearchClient:
        return self.state.meili

    @property
    @override
    def _storage(self) -> AbstractStorage:
        return self.state.storage

    @property
    @override
    def _gd(self) -> GeometryDashClient:
        return self.state.gd
