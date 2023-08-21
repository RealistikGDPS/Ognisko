from __future__ import annotations

from rgdps.constants.levels import LevelSearchFlag
from rgdps.models.level import Level


def calculate_creator_points(level: Level) -> int:
    creator_points = 0

    # One for a rated level
    if level.stars > 0:
        creator_points += 1

    # One for a featured level
    if level.feature_order > 0:
        creator_points += 1

    # One for being rated epic
    if level.search_flags & LevelSearchFlag.EPIC:
        creator_points += 1

    return creator_points
