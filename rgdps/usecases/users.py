from __future__ import annotations

from datetime import datetime
from typing import NamedTuple

from rgdps import repositories
from rgdps.common import hashes
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.friends import FriendStatus
from rgdps.constants.users import UserPrivacySetting
from rgdps.constants.users import UserPrivilegeLevel
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User


# FIXME: Moved to repository
DEFAULT_PRIVILEGES = (
    UserPrivileges.USER_AUTHENTICATE
    | UserPrivileges.USER_PROFILE_PUBLIC
    | UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC
    | UserPrivileges.USER_CP_LEADERBOARD_PUBLIC
    | UserPrivileges.USER_CREATE_USER_COMMENTS
    | UserPrivileges.USER_CHANGE_CREDENTIALS_OWN
    | UserPrivileges.LEVEL_UPLOAD
    | UserPrivileges.LEVEL_UPDATE
    | UserPrivileges.LEVEL_DELETE_OWN
    | UserPrivileges.COMMENTS_POST
    | UserPrivileges.COMMENTS_DELETE_OWN
    | UserPrivileges.COMMENTS_TRIGGER_COMMANDS
    | UserPrivileges.MESSAGES_SEND
    | UserPrivileges.MESSAGES_DELETE_OWN
    | UserPrivileges.FRIEND_REQUESTS_SEND
    | UserPrivileges.FRIEND_REQUESTS_ACCEPT
    | UserPrivileges.FRIEND_REQUESTS_DELETE_OWN
    | UserPrivileges.COMMENTS_LIKE
)


async def register(
    ctx: Context,
    name: str,
    password: str,
    email: str,
) -> User | ServiceError:

    if await repositories.user.check_email_exists(ctx, email):
        return ServiceError.USER_EMAIL_EXISTS
    elif await repositories.user.check_username_exists(ctx, name):
        return ServiceError.USER_USERNAME_EXISTS

    hashed_password = await hashes.hash_bcypt_async(password)

    user = await repositories.user.create(
        ctx,
        username=name,
        password=hashed_password,
        email=email,
    )

    return user


async def authenticate(
    ctx: Context,
    username: str,
    password: str,
) -> User | ServiceError:
    user = await repositories.user.from_name(ctx, username)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    if not await hashes.compare_bcrypt(user.password, password):
        return ServiceError.AUTH_PASSWORD_MISMATCH

    if not user.privileges & UserPrivileges.USER_AUTHENTICATE:
        return ServiceError.AUTH_NO_PRIVILEGE

    return user


class UserPerspective(NamedTuple):
    user: User
    rank: int
    friend_status: FriendStatus


async def get(
    ctx: Context,
    user_id: int,
    is_own: bool = True,
) -> UserPerspective | ServiceError:
    # TODO: Perform Friend Check
    # TODO: Friend Request Check
    # TODO: Messages Check

    user = await repositories.user.from_id(ctx, user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    rank = await repositories.leaderboard.get_star_rank(ctx, user_id)

    if is_own:
        ...

    return UserPerspective(
        user=user,
        rank=rank,
        friend_status=FriendStatus.NONE,
    )


async def update_stats(
    ctx: Context,
    user_id: int,
    stars: int | None = None,
    demons: int | None = None,
    display_type: int | None = None,
    diamonds: int | None = None,
    primary_colour: int | None = None,
    secondary_colour: int | None = None,
    icon: int | None = None,
    ship: int | None = None,
    ball: int | None = None,
    ufo: int | None = None,
    wave: int | None = None,
    robot: int | None = None,
    spider: int | None = None,
    glow: bool | None = None,
    explosion: int | None = None,
    coins: int | None = None,
    user_coins: int | None = None,
    message_privacy: UserPrivacySetting | None = None,
    friend_privacy: UserPrivacySetting | None = None,
    comment_privacy: UserPrivacySetting | None = None,
    youtube_name: str | None = None,
    twitter_name: str | None = None,
    twitch_name: str | None = None,
    update_rank: bool = False,
) -> User | ServiceError:
    # TODO: Validation
    # TODO: Anticheat checks on the user's gains
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.USER_NOT_FOUND

    updated_user = User(
        id=user.id,
        username=user.username,
        email=user.email,
        password=user.password,
        privileges=user.privileges,
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

    if update_rank:
        await repositories.leaderboard.set_star_count(ctx, user.id, updated_user.stars)

    await repositories.user.update_old(ctx, updated_user)
    return updated_user


async def update_privileges(
    ctx: Context,
    user_id: int,
    privileges: UserPrivileges,
) -> User | ServiceError:

    user = await repositories.user.from_id(ctx, user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    # Check if we should remove them from the leaderboard
    if not privileges & UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC:
        await repositories.leaderboard.remove_star_count(ctx, user_id)

    if not privileges & UserPrivileges.USER_CP_LEADERBOARD_PUBLIC:
        # TODO: Add CP leaderboard
        ...

    updated_user = user.copy()
    updated_user.privileges = privileges
    await repositories.user.update_old(ctx, updated_user)
    return updated_user


async def request_status(
    ctx: Context,
    user_id: int,
) -> UserPrivilegeLevel | ServiceError:
    user = await repositories.user.from_id(ctx, user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    if user.privileges & UserPrivileges.USER_REQUEST_MODERATOR:
        return UserPrivilegeLevel.MODERATOR

    elif user.privileges & UserPrivileges.USER_REQUEST_ELDER:
        return UserPrivilegeLevel.ELDER_MODERATOR

    return UserPrivilegeLevel.NONE
