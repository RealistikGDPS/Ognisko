from __future__ import annotations

from enum import Enum

class LeaderboardType(str, Enum):
    STAR = "top"
    CREATOR = "creators"
    STAR_FRIENDS = "friends"
    STAR_RELATIVE = "relative"
