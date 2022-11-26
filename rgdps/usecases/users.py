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

from rgdps import repositories
from rgdps.common import hashes
from rgdps.constants.errors import ServiceError
from rgdps.constants.friends import FriendStatus
from rgdps.constants.privacy import PrivacySetting
from rgdps.constants.responses import GenericResponse
from rgdps.constants.responses import RegisterResponse
from rgdps.models.user import User


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

    if not await hashes.compare_bcrypt(user.password, password):
        return ServiceError.AUTH_PASSWORD_MISMATCH

    # TODO: Privilege check

    return user


class UserPerspective(NamedTuple):
    user: User
    rank: int
    friend_status: FriendStatus


async def get_user_perspective(
    user_id: int,
    perspective: User,
) -> Union[UserPerspective, ServiceError]:
    # TODO: Perform Blocked Check
    # TODO: Perform Privilege Check
    # TODO: Perform Friend Check
    # TODO: Friend Request Check

    user = await repositories.user.from_id(user_id)
    if user is None:
        # TODO: Use something more concise.
        return ServiceError.PROFILE_USER_NOT_FOUND

    rank = await repositories.leaderboard.get_star_rank(user_id)

    return UserPerspective(
        user=user,
        rank=rank,
        friend_status=FriendStatus.NONE,
    )


async def update_stats(
    user: User,
    stars: Optional[int] = None,
    demons: Optional[int] = None,
    display_type: Optional[int] = None,
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
) -> Union[User, ServiceError]:
    # TODO: Validation
    # TODO: Anticheat checks on the user's gains
    # TODO: Perform Privilege Check
    # TODO: Rank calculations
    updated_user = User(
        id=user.id,
        username=user.username,
        email=user.email,
        password=user.password,
        message_privacy=message_privacy or user.message_privacy,
        friend_privacy=friend_privacy or user.friend_privacy,
        comment_privacy=comment_privacy or user.comment_privacy,
        youtube_name=youtube_name or user.youtube_name,
        twitter_name=twitter_name or user.twitter_name,
        twitch_name=twitch_name or user.twitch_name,
        register_ts=user.register_ts,
        stars=stars or user.stars,
        demons=demons or user.demons,
        display_type=display_type or user.display_type,
        diamonds=diamonds or user.diamonds,
        primary_colour=primary_colour or user.primary_colour,
        secondary_colour=secondary_colour or user.secondary_colour,
        icon=icon or user.icon,
        ship=ship or user.ship,
        ball=ball or user.ball,
        ufo=ufo or user.ufo,
        wave=wave or user.wave,
        robot=robot or user.robot,
        spider=spider or user.spider,
        glow=glow or user.glow,
        explosion=explosion or user.explosion,
        coins=coins or user.coins,
        user_coins=user_coins or user.user_coins,
        creator_points=user.creator_points,
    )

    await repositories.leaderboard.set_star_count(user.id, updated_user.stars)

    await repositories.user.update(updated_user)  # TODO: Partial update
    return updated_user
