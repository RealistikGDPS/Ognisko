from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from realistikgdps.constants.privacy import PrivacySetting


@dataclass
class User:
    id: int
    username: str
    email: str
    password: str

    message_privacy: PrivacySetting
    friend_privacy: PrivacySetting
    comment_privacy: PrivacySetting

    youtube_name: Optional[str]
    twitter_name: Optional[str]
    twitch_name: Optional[str]

    register_ts: datetime

    # Stats
    stars: int
    demons: int
    primary_colour: int
    secondary_colour: int
    display_type: int
    icon: int
    ship: int
    ball: int
    ufo: int
    wave: int
    robot: int
    spider: int
    explosion: int
    glow: bool
    creator_points: int
    coins: int
    user_coins: int

    def __str__(self) -> str:
        return f"{self.username} ({self.id})"
