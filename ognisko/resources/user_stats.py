from __future__ import annotations

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel


class UserStatsModel(DatabaseModel):
    __tablename__ = "user_stats"

    star_count = Column(Integer, nullable=False)
    demon_count = Column(Integer, nullable=False)
    moon_count = Column(Integer, nullable=False)
    primary_colour = Column(Integer, nullable=False)
    secondary_colour = Column(Integer, nullable=False)
    glow_colour = Column(Integer, nullable=False)
    use_icon_glow = Column(Boolean, nullable=False)
    displayed_mode = Column(Integer, nullable=False)
    icon_mode = Column(Integer, nullable=False)
    ship_mode = Column(Integer, nullable=False)
    ball_mode = Column(Integer, nullable=False)
    ufo_mode = Column(Integer, nullable=False)
    wave_mode = Column(Integer, nullable=False)
    robot_mode = Column(Integer, nullable=False)
    spider_mode = Column(Integer, nullable=False)
    swing_copter_mode = Column(Integer, nullable=False)
    jetpack_mode = Column(Integer, nullable=False)
    explosion_type = Column(Integer, nullable=False)
    creator_points = Column(Integer, nullable=False)
    gold_coin_count = Column(Integer, nullable=False)
    user_coin_count = Column(Integer, nullable=False)
    diamond_count = Column(Integer, nullable=False)


class UserStatsRepository(BaseRepository[UserStatsModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserStatsModel)
