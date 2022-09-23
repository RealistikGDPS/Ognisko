# Usecases for users and accounts (as they usually heavily overlap).
from __future__ import annotations

from datetime import datetime
from typing import Awaitable
from typing import Callable
from typing import Union

from fastapi import Form
from fastapi import HTTPException

import realistikgdps.state
from realistikgdps import repositories
from realistikgdps.constants.privacy import PrivacySetting
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.constants.responses import LoginResponse
from realistikgdps.constants.responses import RegisterResponse
from realistikgdps.models.user import User
from realistikgdps.typing.types import GDSerialisable
from realistikgdps.usecases import hashes


async def register(
    name: str,
    password: str,
    email: str,
) -> Union[User, RegisterResponse]:
    if not (3 <= len(name) <= 15):
        return RegisterResponse.USERNAME_LENGTH_INVALID
    elif not (6 <= len(password) <= 20):
        return RegisterResponse.PASSWORD_LENGTH_INVALID

    if await repositories.user.check_email_exists(email):
        return RegisterResponse.EMAIL_EXISTS
    elif await repositories.user.check_username_exists(name):
        return RegisterResponse.USERNAME_EXISTS

    hashed_password = await hashes.hash_bcypt_async(password)

    user = User(
        id=0,
        username=name,
        email=email,
        password=hashed_password,
        stars=0,
        demons=0,
        creator_points=0,
        display_type=0,
        primary_colour=0,
        secondary_colour=0,
        coins=0,
        user_coins=0,
        icon=0,
        ship=0,
        ball=0,
        ufo=0,
        wave=0,
        robot=0,
        spider=0,
        explosion=0,
        glow=False,
        message_privacy=PrivacySetting.PUBLIC,
        friend_privacy=PrivacySetting.PUBLIC,
        comment_privacy=PrivacySetting.PUBLIC,
        youtube_name=None,
        twitter_name=None,
        twitch_name=None,
        register_ts=datetime.now(),
    )

    user_id = await repositories.user.create(user)
    user.id = user_id
    return user


def create_gd_profile_object(user: User) -> GDSerialisable:
    return {
        1: user.username,
        2: user.id,
        3: user.stars,
        4: user.demons,
        6: 0,  # TODO: Implement rank
        7: user.id,
        8: user.creator_points,
        9: user.display_type,
        10: user.primary_colour,
        11: user.secondary_colour,
        13: user.coins,
        14: user.icon,
        15: 0,
        16: user.id,
        17: user.user_coins,
        18: user.message_privacy.value,
        19: user.friend_privacy.value,
        20: user.youtube_name or "",
        21: user.icon,
        22: user.ship,
        23: user.ball,
        24: user.ufo,
        25: user.wave,
        26: user.robot,
        28: int(user.glow),
        29: 1,  # Is Registered
        30: 0,  # TODO: Implement rank
        31: 0,  # Friend state (should be handled on case basis)
        43: user.spider,
        44: user.twitter_name or "",
        45: user.twitch_name or "",
        46: 0,  # TODO: Diamonds, which require save data parsing....
        48: user.explosion,
        49: 0,  # TODO: Badge level with privileges.
        50: user.comment_privacy.value,
    }


async def authenticate(
    username: str,
    password: str,
) -> Union[User, LoginResponse]:
    user = await repositories.user.from_name(username)

    if user is None:
        return LoginResponse.FAIL

    if not await hashes.compare_bcrypt_async(user.password, password):
        return LoginResponse.FAIL

    # TODO: Privilege check

    return user


# TODO: add option to replicate https://github.com/RealistikDash/GDPyS/blob/9266cc57c3a4c5d1f51363aa3899ee3c09a23ee8/web/http.py#L338-L341
# FastAPI dependency for seemless authentication.
def authenticate_dependency(
    account_id_alias: str = "accountID",
    gjp_alias: str = "gjp",
) -> Callable[[int, str], Awaitable[User]]:
    async def wrapper(
        account_id: int = Form(..., alias=account_id_alias),
        gjp: str = Form(..., alias=gjp_alias),
    ) -> User:
        user = await repositories.user.from_id(account_id)

        if user is None:
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        if not await hashes.compare_bcrypt_async(
            user.password,
            hashes.decode_gjp(gjp),
        ):
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        return user

    return wrapper
