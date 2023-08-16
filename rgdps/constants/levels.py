from __future__ import annotations

from enum import IntEnum
from enum import IntFlag


class LevelSearchFlag(IntFlag):
    NONE = 0
    EPIC = 1 << 0
    AWARDED = 1 << 1
    MAGIC = 1 << 2


class LevelDifficulty(IntEnum):
    NA = 0
    EASY = 10
    NORMAL = 20
    HARD = 30
    HARDER = 40
    INSANE = 50

    @staticmethod
    def from_stars(stars: int) -> LevelDifficulty:
        return _DIFFICULTY_STAR_MAP.get(
            stars,
            LevelDifficulty.NA,
        )


_DIFFICULTY_STAR_MAP = {
    2: LevelDifficulty.EASY,
    3: LevelDifficulty.EASY,
    4: LevelDifficulty.NORMAL,
    5: LevelDifficulty.HARD,
    6: LevelDifficulty.HARD,
    7: LevelDifficulty.HARDER,
    8: LevelDifficulty.INSANE,
    9: LevelDifficulty.INSANE,
}


class LevelLength(IntEnum):
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4


class LevelDemonDifficulty(IntEnum):
    HARD = 0
    EASY = 3
    MEDIUM = 4
    INSANE = 5
    EXTREME = 6


# Ideas:
# Listed only for friends
class LevelPublicity(IntEnum):
    PUBLIC = 0
    # Levels only accessible through direct ID.
    GLOBAL_UNLISTED = 1
    FRIENDS_UNLISTED = 2


class LevelSearchType(IntEnum):
    SEARCH_QUERY = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    USER_LEVELS = 5
    FEATURED = 6
    MAGIC = 7
    MODERATOR_SENT = 8
    LEVEL_LIST = 9
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    EPIC = 16
    DAILY = 21
    WEEKLY = 22
