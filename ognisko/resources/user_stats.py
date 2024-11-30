from __future__ import annotations

from ognisko.resources._common import DatabaseModel


class UserStatsModel(DatabaseModel):
    user_id: int
    stars: int
    demons: int
    moons: int
    primary_colour: int
    secondary_colour: int
    glow_colour: int
    use_icon_glow: bool
    display_mode: int
    icon_mode: int
    ship_mode: int
    ball_mode: int
    ufo_mode: int
    wave_mode: int
    robot_mode: int
    spider_mode: int
    swing_copter_mode: int
    jetpack_mode: int
    explosion: int
    creator_points: int
    gold_coins: int
    user_coins: int
    diamonds: int
