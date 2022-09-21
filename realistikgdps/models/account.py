from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    id: int
    user_id: int
    name: str
    password: str
    email: str

    messages_blocked: bool  # This should be an enum asthis may also be friends only.
    friend_req_blocked: bool  # This should be an enum asthis may also be friends only.
    comment_history_hidden: bool  # This should be an enum asthis may also be friends only.

    youtube_name: Optional[str]
    twitter_name: Optional[str]
    twitch_name: Optional[str]

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
