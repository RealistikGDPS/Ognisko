from __future__ import annotations

from rgdps.common.context import Context


async def from_level_id(
    ctx: Context,
    level_id: int,
) -> str | None:
    res = await ctx.storage.load(f"levels/{level_id}")

    if res is not None:
        return res.decode()

    return None


async def create(
    ctx: Context,
    level_id: int,
    data: str,
) -> None:
    return await ctx.storage.save(f"levels/{level_id}", data.encode())
