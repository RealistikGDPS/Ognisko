from __future__ import annotations

from ognisko.resources import Context
from ognisko.resources import SaveData
from ognisko.services._common import ServiceError


async def get(ctx: Context, user_id: int) -> SaveData | ServiceError:
    """NOTE: This is memory expensive, with saves reasonably exceeding 200MB."""
    data = await ctx.save_data.from_user_id(user_id)

    if data is None:
        return ServiceError.SAVE_DATA_NOT_FOUND

    return data


async def save(
    ctx: Context,
    user_id: int,
    data: str,
    game_version: int,
    binary_version: int,
) -> None | ServiceError:
    # TODO: Data parsing

    # the 'a' are a placeholder for mappack strings and completed levels.
    # Unfortunately, afaik, they are only achievable through save data parsing
    # which I currently don't want to do.
    data += f";{game_version};{binary_version};a;a"

    await ctx.save_data.create(user_id, data)

    return None
