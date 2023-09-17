from __future__ import annotations

from rgdps import logger
from rgdps.common.context import Context
from rgdps.services.pubsub import RedisPubsubRouter
from rgdps.usecases import levels
from rgdps.usecases import users

router = RedisPubsubRouter()


@router.register("rgdps:ping")
async def ping_handler(ctx: Context, data: bytes) -> None:
    logger.debug(f"Redis ping received with data: {data}")


@router.register("rgdps:levels:sync_meili")
async def level_sync_meili_handler(ctx: Context, _) -> None:
    logger.debug("Synchronising MeiliSearch indexes.")
    await levels.synchronise_search(ctx)


@router.register("rgdps:users:sync_meili")
async def user_sync_meili_handler(ctx: Context, _) -> None:
    logger.debug("Synchronising MeiliSearch indexes.")
    await users.synchronise_search(ctx)
