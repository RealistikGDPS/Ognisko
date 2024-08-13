from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Coroutine
from queue import Queue
from typing import Self

from redis.asyncio import Redis

type PubSubHandler = Callable[[str], Coroutine[None, None, None]]


class RedisClient(Redis):
    """A thin wrapper around the asynchronous Redis client."""

    def __init__(
        self,
        host: str,
        port: int,
        database: int = 0,
        password: str | None = None,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            db=database,
            password=password,
            decode_responses=True,
        )

        self._pubsub_router = RedisPubsubRouter()
        self._tasks: Queue[Awaitable[None]] = Queue(100)
        self._pubsub_listen_lock = asyncio.Lock()

    async def initialise(self) -> Self:
        if not self._pubsub_router.empty:
            self._pubsub_task = self.__create_pubsub_task()

        return await self.initialize()

    def register(
        self,
        channel: str,
    ) -> Callable[[PubSubHandler], PubSubHandler]:
        """Registers a pubsub handler."""
        return self._pubsub_router.register(channel)

    def include_router(self, router: RedisPubsubRouter) -> None:
        self._pubsub_router.merge(router)

    async def __listen_pubsub(
        self,
    ) -> None:
        async with (
            self._pubsub_listen_lock,
            self.pubsub() as pubsub,
        ):
            for channel in self._pubsub_router.route_map():
                await pubsub.subscribe(channel)

            while True:
                message = await pubsub.get_message()
                if message is not None:
                    if message.get("type") != "message":
                        continue

                    handler = self._pubsub_router._get_handler(message["channel"])
                    assert handler is not None

                    # NOTE: Asyncio tasks can get GC'd lmfao.
                    if self._tasks.full():
                        self._tasks.get()

                    self._tasks.put(asyncio.create_task(handler(message["data"])))

                # NOTE: This is a hack to prevent the event loop from blocking.
                await asyncio.sleep(0.1)

    async def __create_pubsub_task(self) -> asyncio.Task:
        return asyncio.create_task(self.__listen_pubsub())


class RedisPubsubRouter:
    """A router for Redis subscriptions."""

    __slots__ = (
        "_routes",
        "_prefix",
    )

    def __init__(
        self,
        *,
        prefix: str = "",
    ) -> None:
        self._routes: dict[str, PubSubHandler] = {}
        self._prefix = prefix

    @property
    def empty(self) -> bool:
        return not self._routes

    def register(
        self,
        channel: str,
    ) -> Callable[[PubSubHandler], PubSubHandler]:
        def decorator(handler: PubSubHandler) -> PubSubHandler:
            channel_name = self._prefix + channel
            self._routes[channel_name] = handler
            return handler

        return decorator

    def merge(self, other: Self) -> None:
        for channel, handler in other.route_map().items():
            if channel in self._routes:
                logging.warning(
                    "Overwritten route when merging Redis routers!",
                    extra={
                        "channel": channel,
                    },
                )
            self._routes[channel] = handler

    def route_map(self) -> dict[str, PubSubHandler]:
        return self._routes

    def _get_handler(self, channel: str) -> PubSubHandler | None:
        return self._routes.get(channel)
