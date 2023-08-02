from __future__ import annotations

from fastapi import Depends
from fastapi import Form
from pydantic import EmailStr

from rgdps import logger
from rgdps.api import responses
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.constants.errors import ServiceError
from rgdps.constants.responses import LoginResponse
from rgdps.constants.users import UserPrivilegeLevel
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User
from rgdps.usecases import users


async def register_post(
    ctx: HTTPContext = Depends(),
    username: str = Form(..., alias="userName", min_length=3, max_length=15),
    email: EmailStr = Form(...),
    password: str = Form(..., min_length=6, max_length=20),
):
    user = await users.register(
        ctx,
        name=username,
        password=password,
        email=email,
    )

    if isinstance(user, ServiceError):
        logger.info(f"Failed to register {username} due to {user!r}.")
        return str(user)

    logger.info(f"{user} has registered!")

    return responses.success()


async def login_post(
    ctx: HTTPContext = Depends(),
    username: str = Form(..., alias="userName", max_length=15),
    password: str = Form(..., max_length=20),
    _: str = Form(..., alias="udid"),
):

    user = await users.authenticate(ctx, username, password)
    if isinstance(user, ServiceError):
        logger.info(f"Failed to login {username} due to {user!r}.")

        if user is ServiceError.AUTH_NO_PRIVILEGE:
            return responses.code(LoginResponse.ACCOUNT_DISABLED)

        return responses.fail()

    logger.info(f"{user} has logged in!")

    return f"{user.id},{user.id}"


async def user_info_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    target_id: int = Form(..., alias="targetAccountID"),
):
    is_own = target_id == user.id
    target = await users.get(ctx, target_id, is_own)

    if isinstance(target, ServiceError):
        logger.info(
            f"Requested to view info of non-existent account {target_id} "
            f"with error {target!r}.",
        )
        return responses.fail()

    # TODO: Move to its own function.
    if (
        (not is_own)
        and (not target.user.privileges & UserPrivileges.USER_PROFILE_PUBLIC)
        and (not user.privileges & UserPrivileges.USER_VIEW_PRIVATE_PROFILE)
    ):
        return responses.fail()

    logger.info(f"Successfully viewed the profile of {target.user}.")

    return gd_obj.dumps(
        gd_obj.create_profile(target.user, target.friend_status, target.rank),
    )


async def user_info_update(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    stars: int = Form(...),
    demons: int = Form(...),
    display_type: int = Form(..., alias="icon"),
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
):

    res = await users.update_stats(
        ctx,
        user.id,
        stars=stars,
        demons=demons,
        display_type=display_type,
        diamonds=diamonds,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        glow=glow,
        explosion=explosion,
        coins=coins,
        user_coins=user_coins,
        update_rank=bool(user.privileges & UserPrivileges.USER_PROFILE_PUBLIC),
    )

    if isinstance(res, ServiceError):
        logger.info(f"Failed to update profile of {user} with error {res!r}.")
        return responses.fail()

    logger.info(f"Successfully updated the profile of {user}.")

    return str(user.id)


async def user_settings_update(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    youtube_name: str = Form(..., alias="yt"),
    twitter_name: str = Form(..., alias="twitter"),
    twitch_name: str = Form(..., alias="twitch"),
):
    result = await users.update_stats(
        ctx,
        user.id,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
    )

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to update settings of {user} with error {result!r}.",
        )
        return responses.fail()

    logger.info(f"Successfully updated settings of {user}.")
    return responses.success()


async def request_status_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
):
    result = await users.request_status(ctx, user.id)

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to get request status of {user} with error {result!r}.",
        )
        return responses.fail()

    logger.info(f"Successfully got request status of {user}.")

    if result is UserPrivilegeLevel.NONE:
        return responses.fail()

    return str(result)
