from __future__ import annotations

import os

from rgdps.common.context import Context
from rgdps.config import config


def from_user_id_as_path(ctx: Context, user_id: int) -> str | None:
    directory = f"{config.data_saves}/{user_id}"

    if not os.path.exists(directory):
        return None

    return directory


def from_user_id(ctx: Context, user_id: int) -> str | None:
    directory = from_user_id_as_path(ctx, user_id)

    if directory is None:
        return None

    with open(directory) as f:
        return f.read()


def create(ctx: Context, user_id: int, data: str) -> None:
    directory = f"{config.data_saves}/{user_id}"

    with open(directory, "w") as file:
        file.write(data)
