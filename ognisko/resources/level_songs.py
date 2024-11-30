from __future__ import annotations

from ognisko.resources._common import DatabaseModel


class LevelSongAssignModel(DatabaseModel):
    level_id: int
    song_id: int
    is_primary: bool
