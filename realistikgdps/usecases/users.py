# Usecases for users and accounts (as they usually heavily overlap).
from __future__ import annotations

from datetime import datetime
from typing import Awaitable
from typing import Callable
from typing import NamedTuple
from typing import Optional
from typing import Union

from fastapi import Form
from fastapi import HTTPException

from realistikgdps import repositories
from realistikgdps.common import hashes
from realistikgdps.constants.errors import ServiceError
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
) -> Union[User, ServiceError]:
    user = await repositories.user.from_name(username)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    if not await hashes.compare_bcrypt_async(user.password, password):
        return ServiceError.AUTH_PASSWORD_MISMATCH

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
) -> Union[UserPerspective, ServiceError]:
    # TODO: Perform Blocked Check
    # TODO: Perform Privilege Check
    # TODO: Perform Friend Check
    # TODO: Friend Request Check

    user = await repositories.user.from_id(user_id)
    if user is None:
        # TODO: Use something more concise.
        return ServiceError.PROFILE_USER_NOT_FOUND

    return UserPerspective(
        user=user,
        friend_status=FriendStatus.NONE,
    )


async def update_stats(
    user: User,
    stars: Optional[int] = None,
    demons: Optional[int] = None,
    display_icon: Optional[int] = None,
    diamonds: Optional[int] = None,
    primary_colour: Optional[int] = None,
    secondary_colour: Optional[int] = None,
    icon: Optional[int] = None,
    ship: Optional[int] = None,
    ball: Optional[int] = None,
    ufo: Optional[int] = None,
    wave: Optional[int] = None,
    robot: Optional[int] = None,
    spider: Optional[int] = None,
    glow: Optional[bool] = None,
    explosion: Optional[int] = None,
    coins: Optional[int] = None,
    user_coins: Optional[int] = None,
    message_privacy: Optional[PrivacySetting] = None,
    friend_privacy: Optional[PrivacySetting] = None,
    comment_privacy: Optional[PrivacySetting] = None,
    youtube_name: Optional[str] = None,
    twitter_name: Optional[str] = None,
    twitch_name: Optional[str] = None,
) -> Optional[ServiceError]:
    # TODO: Validation
    # TODO: Anticheat checks on the user's gains
    # TODO: Perform Privilege Check
    # TODO: Rank calculations
    user.stars = stars or user.stars
    user.demons = demons or user.demons
    user.display_type = display_icon or user.display_type
    user.diamonds = diamonds or user.diamonds
    user.primary_colour = primary_colour or user.primary_colour
    user.secondary_colour = secondary_colour or user.secondary_colour
    user.icon = icon or user.icon
    user.ship = ship or user.ship
    user.ball = ball or user.ball
    user.ufo = ufo or user.ufo
    user.wave = wave or user.wave
    user.robot = robot or user.robot
    user.spider = spider or user.spider
    user.glow = glow or user.glow
    user.explosion = explosion or user.explosion
    user.coins = coins or user.coins
    user.user_coins = user_coins or user.user_coins
    user.message_privacy = message_privacy or user.message_privacy
    user.friend_privacy = friend_privacy or user.friend_privacy
    user.comment_privacy = comment_privacy or user.comment_privacy
    user.youtube_name = youtube_name or user.youtube_name
    user.twitter_name = twitter_name or user.twitter_name
    user.twitch_name = twitch_name or user.twitch_name

    await repositories.user.update(user)  # TODO: Partial update
