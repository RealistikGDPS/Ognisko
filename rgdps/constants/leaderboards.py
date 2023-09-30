from __future__ import annotations

from enum import Enum


class LeaderboardType(str, Enum):
    STAR = "top"
    CREATOR = "creators"
    STAR_FRIENDS = "friends"
    STAR_RELATIVE = "relative"


STAR_PRIVILEGES = (
    UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC | UserPrivileges.USER_PROFILE_PUBLIC
)

CREATOR_PRIVILEGES = (
    UserPrivileges.USER_CREATOR_LEADERBOARD_PUBLIC | UserPrivileges.USER_PROFILE_PUBLIC
)
