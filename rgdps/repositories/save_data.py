from __future__ import annotations

import os

from rgdps import logger
from rgdps.common.context import Context
from rgdps.config import config


def _from_user_id_local(ctx: Context, user_id: int) -> str | None:
    directory = f"{config.data_saves}/{user_id}"

    if not os.path.exists(directory):
        return None

    with open(directory) as f:
        return f.read()


def _create_local(ctx: Context, user_id: int, data: str) -> None:
    directory = f"{config.data_saves}/{user_id}"

    with open(directory, "w") as file:
        file.write(data)


async def _create_s3(
    ctx: Context,
    user_id: int,
    data: str,
) -> None:
    assert ctx.s3 is not None, "S3 client not available"
    await ctx.s3.put_object(
        Bucket=config.s3_bucket,
        Key=f"saves/{user_id}",
        Body=data,
    )


async def _from_user_id_s3(
    ctx: Context,
    user_id: int,
) -> str | None:
    assert ctx.s3 is not None, "S3 client not available"
    try:
        response = await ctx.s3.get_object(
            Bucket=config.s3_bucket,
            Key=f"saves/{user_id}",
        )
    except ctx.s3.exceptions.NoSuchKey:
        return None

    return (await response["Body"].read()).decode()


async def from_user_id(
    ctx: Context,
    user_id: int,
) -> str | None:
    if config.s3_enabled:
        logger.debug("Loading from S3")
        return await _from_user_id_s3(ctx, user_id)

    logger.debug("Loading locally")
    return _from_user_id_local(ctx, user_id)


async def create(
    ctx: Context,
    user_id: int,
    data: str,
) -> None:
    if config.s3_enabled:
        logger.debug("Saving to S3")
        await _create_s3(ctx, user_id, data)
    else:
        logger.debug("Saving locally")
        _create_local(ctx, user_id, data)
