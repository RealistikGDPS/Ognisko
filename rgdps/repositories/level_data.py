from __future__ import annotations

import os
from typing import Optional

from rgdps.common.context import Context
from rgdps.config import config


def from_level_id_as_path(ctx: Context, level_id: int) -> Optional[str]:
    path = f"{config.data_levels}/{level_id}"

    if not os.path.exists(path):
        return None

    return path


def from_level_id(ctx: Context, level_id: int) -> Optional[str]:
    """NOTE: These can get quite large, usually ~10MB but some can exceed 100MB."""
    path = from_level_id_as_path(ctx, level_id)

    if path is None:
        return None

    with open(path) as f:
        return f.read()


def create(ctx: Context, level_id: int, data: str) -> None:
    path = f"{config.data_levels}/{level_id}"

    with open(path, "w") as f:
        f.write(data)
