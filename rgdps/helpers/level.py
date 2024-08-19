from __future__ import annotations

import base64

import xor_cipher

from rgdps.constants.levels import LevelSearchFlag


def calculate_creator_points(
    stars: int,
    feature_order: int,
    search_flags: LevelSearchFlag,
) -> int:
    creator_points = 0

    # One for a rated level
    if stars > 0:
        creator_points += 1

    # One for a featured level
    if feature_order > 0:
        creator_points += 1

    # One for being rated epic
    if search_flags & LevelSearchFlag.EPIC:
        creator_points += 1

    if search_flags & LevelSearchFlag.LEGENDARY:
        creator_points += 1

    if search_flags & LevelSearchFlag.MYTHICAL:
        creator_points += 1

    return creator_points


LEVEL_PASSWORD_XOR_KEY = b"26364"


def hash_level_password(password: int) -> str:
    if not password:
        return "0"

    xor_password = xor_cipher.cyclic_xor(
        data=str(password).encode(),
        key=LEVEL_PASSWORD_XOR_KEY,
    )

    return base64.urlsafe_b64encode(xor_password).decode()
