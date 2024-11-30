from __future__ import annotations

from ognisko.resources._common import DatabaseModel


class LevelSongAssignModel(DatabaseModel):
    level_id: int
    sound_effect_id: int
