from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from realistikgdps.constants.privacy import PrivacySetting


@dataclass
class Account:
    id: int
    user_id: int
    name: str
    password: str
    email: str

    messages: PrivacySetting
    friend_requests: PrivacySetting
    comment_history: PrivacySetting

    youtube_name: Optional[str]
    twitter_name: Optional[str]
    twitch_name: Optional[str]

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
