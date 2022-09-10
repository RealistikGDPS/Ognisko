from __future__ import annotations

from typing import Optional

import realistikgdps.state
from realistikgdps.models.user import User


async def from_db(user_id: int) -> Optional[User]:
    user_db = await realistikgdps.state.services.database.fetch_one(
        "SELECT userID, extID, userName, stars, demons, color1, color2, "
        "iconType, coins, userCoins, accIcon, accShip, accBall, accBird, "
        "accDart, accRobot, accGlow, accSpider, creatorPoints, isBanned, "
        "isCreatorBanned FROM users WHERE userID = :user_id",
        {
            "user_id": user_id,
        },
    )

    if user_db is None:
        return None

    return User(
        id=user_db["userID"],
        ext_id=user_db["extID"],
        name=user_db["userName"],
        stars=user_db["stars"],
        demons=user_db["demons"],
        primary_colour=user_db["color1"],
        secondary_colour=user_db["color2"],
        display_type=user_db["iconType"],
        coins=user_db["coins"],
        user_coins=user_db["userCoins"],
        icon=user_db["accIcon"],
        ship=user_db["accShip"],
        ball=user_db["accBall"],
        ufo=user_db["accBird"],
        wave=user_db["accDart"],
        robot=user_db["accRobot"],
        glow=user_db["accGlow"] == 1,
        spider=user_db["accSpider"],
        creator_points=user_db["creatorPoints"],
        player_lb_ban=user_db["isBanned"] == 1,
        creator_lb_ban=user_db["isCreatorBanned"] == 1,
    )


async def into_db(user: User) -> int:
    return await realistikgdps.state.services.database.execute(
        "INSERT INTO users (extID, userName, stars, demons, color1, color2, "
        "iconType, coins, userCoins, accIcon, accShip, accBall, accBird, "
        "accDart, accRobot, accGlow, accSpider, creatorPoints, isBanned, "
        "isCreatorBanned) VALUES (:ext_id, :name, :stars, :demons, :primary_colour, "
        ":secondary_colour, :display_type, :coins, :user_coins, :icon, :ship, :ball, "
        ":ufo, :wave, :robot, :glow, :spider, :creator_points, :player_lb_ban, "
        ":creator_lb_ban)",
        {
            "ext_id": user.ext_id,
            "name": user.name,
            "stars": user.stars,
            "demons": user.demons,
            "primary_colour": user.primary_colour,
            "secondary_colour": user.secondary_colour,
            "display_type": user.display_type,
            "coins": user.coins,
            "user_coins": user.user_coins,
            "icon": user.icon,
            "ship": user.ship,
            "ball": user.ball,
            "ufo": user.ufo,
            "wave": user.wave,
            "robot": user.robot,
            "glow": user.glow,
            "spider": user.spider,
            "creator_points": user.creator_points,
            "player_lb_ban": user.player_lb_ban,
            "creator_lb_ban": user.creator_lb_ban,
        },
    )


def from_cache(user_id: int) -> Optional[User]:
    return realistikgdps.state.repositories.user_repo.get(user_id)


def into_cache(user: User) -> None:
    realistikgdps.state.repositories.user_repo[user.id] = user


async def from_id(user_id: int) -> Optional[User]:
    """Attempts to fetch the user first from cache, then from database by their
    user ID."""

    if user := from_cache(user_id):
        return user

    if user := await from_db(user_id):
        into_cache(user)
        return user

    return None
