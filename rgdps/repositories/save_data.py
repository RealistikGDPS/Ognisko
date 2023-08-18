from __future__ import annotations

from rgdps.common.context import Context


async def from_user_id(
    ctx: Context,
    user_id: int,
) -> str | None:
    res = await ctx.storage.load(f"saves/{user_id}")

    if res is not None:
        return res.decode()

    return None


async def create(
    ctx: Context,
    user_id: int,
    data: str,
) -> None:
    return await ctx.storage.save(f"saves/{user_id}", data.encode())
