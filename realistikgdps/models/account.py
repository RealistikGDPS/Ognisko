from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    id: int
    name: str
    password: str
    email: str

    messages_blocked: bool
    friend_req_blocked: bool
    comment_history_hidden: bool

    youtube_name: Optional[str]
    twitter_name: Optional[str]
    twitch_name: Optional[str]
