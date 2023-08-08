from __future__ import annotations

from rgdps import logger
from rgdps.common.context import Context
from rgdps.services.pubsub import RedisPubsubRouter
from rgdps.usecases import levels

router = RedisPubsubRouter()


@router.register("rgdps:ping")
async def ping_handler(ctx: Context, data: bytes) -> None:
    logger.debug(f"Redis ping received. {ctx.meili!r}")


@router.register("rgdps:levels:sync_meili")
async def sync_meili_handler(ctx: Context, data: bytes) -> None:
    logger.debug("Synchronising MeiliSearch indexes.")
    await levels.synchronise_search(ctx)
