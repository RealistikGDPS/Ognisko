from __future__ import annotations

from typing import Optional

from rgdps.common import hashes
from rgdps.state import repositories
from rgdps.state import services


async def hash_from_id(user_id: int) -> Optional[str]:
    hash_db = await services.database.fetch_val(
        "SELECT password FROM users WHERE id = :user_id",
        {
            "user_id": user_id,
        },
    )

    return hash_db


async def compare_bcrypt(hash_db: str, password: str) -> bool:
    password_cached = await repositories.password_cache.get(hash_db)
    if password_cached is not None:
        return password_cached == password

    res = await hashes.compare_bcrypt(hash_db, password)

    if res:
        await repositories.password_cache.set(hash_db, password)

    return res


async def compare_bcrypt_gjp(hash_db: str, password_gjp: str) -> bool:
    return await compare_bcrypt(
        hash_db,
        hashes.decode_gjp(password_gjp),
    )
