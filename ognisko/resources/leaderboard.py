from __future__ import annotations

from ognisko.adapters import RedisClient


class LeaderboardRepository:
    __slots__ = ("_redis",)

    def __init__(self, redis: RedisClient) -> None:
        self._redis = redis

    async def get_star_rank(self, user_id: int) -> int | None:
        redis_rank = await self._redis.zrevrank(
            "ognisko:leaderboards:stars",
            user_id,
        )

        if redis_rank is None:
            return None

        return redis_rank + 1

    async def get_creator_rank(self, user_id: int) -> int | None:
        redis_rank = await self._redis.zrevrank(
            "ognisko:leaderboards:creators",
            user_id,
        )

        if redis_rank is None:
            return None

        return redis_rank + 1

    async def set_star_count(self, user_id: int, stars: int) -> None:
        await self._redis.zadd(
            "ognisko:leaderboards:stars",
            {str(user_id): stars},  # is str necessary?
        )

    async def remove_star_count(self, user_id: int) -> None:
        await self._redis.zrem(
            "ognisko:leaderboards:stars",
            user_id,
        )

    async def set_creator_count(self, user_id: int, stars: int) -> None:
        await self._redis.zadd(
            "ognisko:leaderboards:creators",
            {str(user_id): stars},  # is str necessary?
        )

    async def remove_creator_count(self, user_id: int) -> None:
        await self._redis.zrem(
            "ognisko:leaderboards:creators",
            user_id,
        )

    async def get_top_stars_paginated(
        self,
        page: int,
        page_size: int,
    ) -> list[int]:
        top_stars = await self._redis.zrevrange(
            "ognisko:leaderboards:stars",
            page * page_size,
            (page + 1) * page_size,
        )
        return [int(top_star) for top_star in top_stars]

    async def get_top_creators_paginated(
        self,
        page: int,
        page_size: int,
    ) -> list[int]:
        top_creators = await self._redis.zrevrange(
            "ognisko:leaderboards:creators",
            page * page_size,
            (page + 1) * page_size,
        )
        return [int(top_creator) for top_creator in top_creators]
