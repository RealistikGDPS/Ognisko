from __future__ import annotations

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class LevelFeature(StrEnum):
    NONE = "none"
    FEATURE = "feature"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class LevelDifficulty(StrEnum):
    NA = "na"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    HARDER = "harder"
    INSANE = "insane"


class LevelLength(StrEnum):
    TINY = "tiny"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    XL = "xl"
    PLATFORMER = "platformer"


class LevelDemonDifficulty(StrEnum):
    HARD = "hard"
    EASY = "easy"
    MEDIUM = "medium"
    INSANE = "insane"
    EXTREME = "extreme"


class LevelPublicity(StrEnum):
    PUBLIC = "public"
    GLOBAL_UNLISTED = "global_unlisted"
    FRIENDS_UNLISTED = "friends_unlisted"
    FRIENDS_SEARCHABLE = "friends_searchable"


class CustomLevelModel(DatabaseModel):
    __tablename__ = "levels"

    name = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    version = Column(Integer, nullable=False)
    length = Column(Enum(LevelLength), nullable=False)
    is_two_player = Column(Boolean, nullable=False)
    publicity = Column(Enum(LevelPublicity), nullable=False)
    render_str = Column(String, nullable=False)  # Officially called extra string
    created_with_game_version = Column(Integer, nullable=False)
    created_with_binary_version = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    original_level_id = Column(Integer, nullable=True)

    # Statistics
    download_count = Column(Integer, nullable=False)
    like_count = Column(Integer, nullable=False)
    star_reward = Column(Integer, nullable=False)
    difficulty_rating = Column(Enum(LevelDifficulty), nullable=False)
    demon_difficulty_rating = Column(Enum(LevelDemonDifficulty), nullable=True)
    coin_count = Column(Integer, nullable=False)
    has_coins_verified = Column(Boolean, nullable=False)
    requested_star_reward = Column(Integer, nullable=False)
    feature_priority = Column(Integer, nullable=False)
    featured_status = Column(Enum(LevelFeature), nullable=False)
    is_low_detail_mode_available = Column(Boolean, nullable=False)
    object_count = Column(Integer, nullable=False)
    building_time = Column(Integer, nullable=False)

    is_update_locked = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, nullable=False)


class CustomLevelRepository(BaseRepository[CustomLevelModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, CustomLevelModel)


"""
    # TODO: Move LOL
    # A function primarily used for some recommendation algorithms that returns a list of levels
    # ordered by how well received they are, assessed using a formula..
    async def get_well_received(
        self,
        minimum_stars: int,
        minimum_length: LevelLength,
        maximum_stars: int = 0,
        maximum_demon_rating: LevelDemonDifficulty = LevelDemonDifficulty.EXTREME,
        excluded_level_ids: list[
            int
        ] = [],  # The list isnt mutable, so we can set it to an empty list.
        limit: int = 100,
    ) -> list[int]:
        # BOTCH! Avoiding a sql syntax error.
        if not excluded_level_ids:
            excluded_level_ids = [0]

        # The formula in the order clause is made to emphasis lower downloads, but still have a
        # significant impact on likes.
        values = await self._mysql.fetch_all(
            "SELECT id FROM levels WHERE stars >= :minimum_stars AND stars <= :maximum_stars "
            "AND demon_difficulty <= :maximum_demon_rating AND length >= :minimum_length "
            "AND id NOT IN :excluded_level_ids AND deleted = 0 ORDER BY (SQRT(downloads) / likes) DESC "
            "LIMIT :limit",
            {
                "minimum_stars": minimum_stars,
                "maximum_stars": maximum_stars,
                "maximum_demon_rating": maximum_demon_rating.value,
                "minimum_length": minimum_length.value,
                "excluded_level_ids": tuple(excluded_level_ids),
                "limit": limit,
            },
        )

        return [x["id"] for x in values]
"""
