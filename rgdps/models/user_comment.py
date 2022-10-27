from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserComment:
    id: int
    user_id: int
    content: str
    likes: int
    post_ts: datetime
    deleted: bool
