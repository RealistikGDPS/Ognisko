from __future__ import annotations

from ognisko import logger
from ognisko.adapters import RedisPubsubRouter
from ognisko.resources import Context
from ognisko.services import leaderboards
from ognisko.services import levels
from ognisko.services import users

router = RedisPubsubRouter()

# XXX: This is really hacky.
redis_context: Context


def inject_context(ctx: Context) -> None:
    global redis_context
    redis_context = ctx


def context() -> Context:
    return redis_context


# TODO: Look into creating unique UUIDs for each pubsub message,
# for easier identification in logging.


@router.register("ognisko:ping")
async def ping_handler(data: str) -> None:
    logger.debug(
        "Redis received a ping.",
        extra={
            "data": data,
        },
    )


@router.register("ognisko:levels:sync_meili")
async def level_sync_meili_handler(_) -> None:
    ctx = context()
    logger.debug("Redis received a level sync request.")
    await levels.synchronise_search(ctx)


@router.register("ognisko:users:sync_meili")
async def user_sync_meili_handler(_) -> None:
    ctx = context()
    logger.debug("Redis received a user sync request.")
    await users.synchronise_search(ctx)


@router.register("ognisko:leaderboards:sync_stars")
async def leaderboard_sync_stars_handler(_) -> None:
    ctx = context()
    logger.debug("Redis received a leaderboard sync request.")
    await leaderboards.synchronise_top_stars(ctx)


@router.register("ognisko:leaderboards:sync_creators")
async def leaderboard_sync_creators_handler(_) -> None:
    ctx = context()
    logger.debug("Redis received a leaderboard sync request.")
    await leaderboards.synchronise_top_creators(ctx)
