from __future__ import annotations

import os
from typing import Optional

from realistikgdps.config import config


def from_level_id_as_path(level_id: int) -> Optional[str]:
    path = f"{config.data_levels}/{level_id}"

    if not os.path.exists(path):
        return None

    return path


def from_level_id(level_id: int) -> Optional[str]:
    path = from_level_id_as_path(level_id)

    if path is None:
        return None

    with open(path) as f:
        return f.read()


def create(level_id: int, data: str) -> None:
    path = f"{config.data_levels}/{level_id}"

    with open(path, "w") as f:
        f.write(data)
