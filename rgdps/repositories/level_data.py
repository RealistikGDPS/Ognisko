from __future__ import annotations

import os

from rgdps.common.context import Context
from rgdps.config import config


def _from_id_local(ctx: Context, level_id: int) -> str | None:
    path = f"{config.data_levels}/{level_id}"

    if not os.path.exists(path):
        return None

    with open(path) as f:
        return f.read()


def _create_local(ctx: Context, level_id: int, data: str) -> None:
    path = f"{config.data_levels}/{level_id}"

    with open(path, "w") as f:
        f.write(data)


async def _create_s3(
    ctx: Context,
    level_id: int,
    data: str,
) -> None:
    assert ctx.s3 is not None, "S3 client not available"
    await ctx.s3.put_object(
        Bucket=config.s3_bucket,
        Key=f"levels/{level_id}",
        Body=data,
    )


async def _from_id_s3(ctx: Context, level_id: int) -> str | None:
    assert ctx.s3 is not None, "S3 client not available"
    try:
        response = await ctx.s3.get_object(
            Bucket=config.s3_bucket,
            Key=f"levels/{level_id}",
        )
    except ctx.s3.exceptions.NoSuchKey:
        return None

    return (await response["Body"].read()).decode()


async def from_level_id(
    ctx: Context,
    level_id: int,
) -> str | None:
    if config.s3_enabled:
        return await _from_id_s3(ctx, level_id)

    return _from_id_local(ctx, level_id)


async def create(
    ctx: Context,
    level_id: int,
    data: str,
) -> None:
    if config.s3_enabled:
        await _create_s3(ctx, level_id, data)
    else:
        _create_local(ctx, level_id, data)
