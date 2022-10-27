from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from rgdps.constants.levels import LevelDemonDifficulty
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlags


@dataclass
class Level:
    id: int
    name: str
    user_id: int
    description: str
    custom_song_id: Optional[int]
    official_song_id: Optional[int]
    version: int
    length: LevelLength
    two_player: bool
    publicity: LevelPublicity
    render_str: str  # Officially called extra string
    game_version: int
    binary_version: int
    upload_ts: datetime
    original_id: Optional[int]

    # Statistics
    downloads: int
    likes: int
    stars: int
    difficulty: LevelDifficulty
    demon_difficulty: Optional[LevelDemonDifficulty]
    coins: int
    coins_verified: bool
    requested_stars: int
    feature_order: int
    search_flags: LevelSearchFlags
    low_detail_mode: bool
    object_count: int
    copy_password: int
    building_time: int
    update_locked: bool
    deleted: bool

    # verification_replay: str
