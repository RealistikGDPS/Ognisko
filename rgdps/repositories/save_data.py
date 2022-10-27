from __future__ import annotations

import os
from typing import Optional

from rgdps.config import config


def from_user_id_as_path(user_id: int) -> Optional[str]:
    directory = f"{config.data_saves}/{user_id}"

    if not os.path.exists(directory):
        return None

    return directory


def from_user_id(user_id: int) -> Optional[str]:
    directory = from_user_id_as_path(user_id)

    if directory is None:
        return None

    with open(directory) as f:
        return f.read()


def create(user_id: int, data: str) -> None:
    directory = f"{config.data_saves}/{user_id}"

    with open(directory, "w") as file:
        file.write(data)
