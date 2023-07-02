from __future__ import annotations

from typing import Optional

from rgdps.common import hashes
from rgdps.common.context import Context


async def hash_from_id(ctx: Context, user_id: int) -> Optional[str]:
    hash_db = await ctx.mysql.fetch_val(
        "SELECT password FROM users WHERE id = :user_id",
        {
            "user_id": user_id,
        },
    )

    return hash_db


async def compare_bcrypt(ctx: Context, hash_db: str, password: str) -> bool:
    password_cached = await ctx.password_cache.get(hash_db)
    if password_cached is not None:
        return password_cached == password

    res = await hashes.compare_bcrypt(hash_db, password)

    if res:
        await ctx.password_cache.set(hash_db, password)

    return res
