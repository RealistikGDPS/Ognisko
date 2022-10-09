from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Level:
    id: int
    name: str
    user_id: int
    description: str
    song_id: Optional[int]  # Used for custom songs
    track_id: Optional[int]  # Used for official songs
    version: int
    length: int  # TODO: Enum
    two_player: bool
    unlisted: bool
    extra_str: str  # Officially called this. Used to help with rendering.
    # verification_replay: str
    game_version: int
    binary_version: int
    upload_ts: datetime
    original_id: Optional[int]

    # Statistics
    downloads: int
    likes: int
    stars: int
    difficulty: int  # TODO: Enum
    demon_difficulty: Optional[int]  # TODO: Enum
    coins: int
    coins_verified: bool
    requested_stars: int
    feature_order: int
    # TODO: Level ranking status (epic, features, magic, awarded)
    ldm: bool
    object_count: int
    copy_password: int
    building_time: int
    update_locked: bool
