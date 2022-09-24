# Usecases for users and accounts (as they usually heavily overlap).
from __future__ import annotations

from datetime import datetime
from typing import Awaitable
from typing import Callable
from typing import NamedTuple
from typing import Union

from fastapi import Form
from fastapi import HTTPException

from realistikgdps import repositories
from realistikgdps.common import hashes
from realistikgdps.constants.friends import FriendStatus
from realistikgdps.constants.privacy import PrivacySetting
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.constants.responses import LoginResponse
from realistikgdps.constants.responses import RegisterResponse
from realistikgdps.models.user import User


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
        diamonds=0,
    )

    user_id = await repositories.user.create(user)
    user.id = user_id
    return user


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


class UserPerspective(NamedTuple):
    user: User
    friend_status: FriendStatus


async def get_user_perspective(
    user_id: int,
    perspective_user: User,
) -> Union[UserPerspective, GenericResponse]:
    # TODO: Perform Blocked Check
    # TODO: Perform Privilege Check
    # TODO: Perform Friend Check

    user = await repositories.user.from_id(user_id)
    if user is None:
        # TODO: Use something more concise.
        return GenericResponse.FAIL

    return UserPerspective(
        user=user,
        friend_status=FriendStatus.NONE,
    )
