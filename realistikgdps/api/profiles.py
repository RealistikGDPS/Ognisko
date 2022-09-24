from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from realistikgdps import logger
from realistikgdps import repositories
from realistikgdps.common import gd_obj
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.models.user import User
from realistikgdps.usecases import users
from realistikgdps.usecases.users import authenticate_dependency


async def view_user_info(
    target_id: int = Form(..., alias="targetAccountID"),
    user: User = Depends(authenticate_dependency()),
) -> str:
    target = await users.get_user_perspective(target_id, user)

    if isinstance(target, GenericResponse):
        logger.info(f"Requested to view info of non-existent account {target_id}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully viewed the profile of {target.user}.")

    return gd_obj.dumps(
        gd_obj.create_gd_profile(target.user, target.friend_status),
    )


async def update_user_info(
    user: User = Depends(authenticate_dependency()),
    stars: int = Form(...),
    demons: int = Form(...),
    display_icon: int = Form(..., alias="icon"),
    diamonds: int = Form(...),
    primary_colour: int = Form(..., alias="color1"),
    secondary_colour: int = Form(..., alias="color2"),
    icon: int = Form(..., alias="accIcon"),
    ship: int = Form(..., alias="accShip"),
    ball: int = Form(..., alias="accBall"),
    ufo: int = Form(..., alias="accBird"),
    wave: int = Form(..., alias="accDart"),
    robot: int = Form(..., alias="accRobot"),
    spider: int = Form(..., alias="accSpider"),
    glow: bool = Form(..., alias="accGlow"),
    explosion: int = Form(..., alias="accExplosion"),
    coins: int = Form(...),
    user_coins: int = Form(..., alias="userCoins"),
) -> str:

    # TODO: Make into a usecase.
    user.stars = stars
    user.demons = demons
    user.display_type = display_icon
    user.diamonds = diamonds
    user.primary_colour = primary_colour
    user.secondary_colour = secondary_colour
    user.icon = icon
    user.ship = ship
    user.ball = ball
    user.ufo = ufo
    user.wave = wave
    user.robot = robot
    user.spider = spider
    user.glow = glow
    user.explosion = explosion
    user.coins = coins
    user.user_coins = user_coins

    await repositories.user.update(user)

    logger.info(f"Successfully updated the profile of {user}.")

    return str(user.id)
