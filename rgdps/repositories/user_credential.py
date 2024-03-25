from __future__ import annotations

from rgdps.common.context import Context
from rgdps.constants.user_credentials import CredentialVersion
from rgdps.models.user_credential import UserCredential
from rgdps.common import modelling


ALL_FIELDS = modelling.get_model_fields(UserCredential)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(CUSTOMISABLE_FIELDS)


async def create(
    ctx: Context,
    user_id: int,
    credential_version: CredentialVersion,
    value: str,
) -> UserCredential:
    credential = UserCredential(
        id=0,
        user_id=user_id,
        version=credential_version,
        value=value,
    )
    credential.id = await ctx.mysql.execute(
        f"INSERT INTO user_credentials ({_CUSTOMISABLE_FIELDS_COMMA}) "
        f"VALUES ({_CUSTOMISABLE_FIELDS_COLON})",
        credential.as_dict(include_id=False),
    )

    return credential


async def from_user_id(
    ctx: Context,
    user_id: int,
) -> UserCredential | None:
    res = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_credentials WHERE user_id = :user_id "
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
