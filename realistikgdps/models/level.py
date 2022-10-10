from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from realistikgdps.constants.levels import LevelDemonDifficulty
from realistikgdps.constants.levels import LevelDifficulty
from realistikgdps.constants.levels import LevelLength
from realistikgdps.constants.levels import LevelPublicity
from realistikgdps.constants.levels import LevelSearchFlags


@dataclass
class Level:
    id: int
    name: str
    user_id: int
    description: str
    song_id: Optional[int]  # Used for custom songs
    track_id: Optional[int]  # Used for official songs
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
    ldm: bool
    object_count: int
    copy_password: int
    building_time: int
    update_locked: bool

    # verification_replay: str
