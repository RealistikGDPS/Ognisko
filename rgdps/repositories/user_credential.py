from __future__ import annotations

from rgdps.common.context import Context
from rgdps.constants.user_credentials import CredentialVersion
from rgdps.models.user_credential import UserCredential


async def create(
    ctx: Context,
    user_id: int,
    credential_version: CredentialVersion,
    value: str,
) -> UserCredential:
    credential_id = await ctx.mysql.execute(
        "INSERT INTO user_credentials (user_id, version, value) "
        "VALUES (:user_id, :version, :value)",
        {"user_id": user_id, "version": credential_version.value, "value": value},
    )

    return UserCredential(
        id=credential_id,
        user_id=user_id,
        version=credential_version,
        value=value,
    )


async def from_user_id(
    ctx: Context,
    user_id: int,
) -> UserCredential | None:
    res = await ctx.mysql.fetch_one(
        "SELECT id, user_id, version, value FROM user_credentials WHERE user_id = :user_id "
        "ORDER BY id DESC LIMIT 1",
        {"user_id": user_id},
    )

    if not res:
        return None

    return UserCredential.from_mapping(res)


async def delete_from_id(
    ctx: Context,
    credential_id: int,
) -> None:
    await ctx.mysql.execute(
        "DELETE FROM user_credentials WHERE id = :credential_id",
        {"credential_id": credential_id},
    )


async def delete_from_user_id(
    ctx: Context,
    user_id: int,
) -> None:
    await ctx.mysql.execute(
        "DELETE FROM user_credentials WHERE user_id = :user_id",
        {"user_id": user_id},
    )
