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
from rgdps.constants.users import UserRelationshipType
from rgdps.models.friend_request import FriendRequest
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
    friend_request: FriendRequest | None
    messages_count: int
    friend_request_count: int
    friend_count: int


async def get(
    ctx: Context,
    request_user_id: int,
    user_id: int,
    is_own: bool = True,
) -> UserPerspective | ServiceError:

    user = await repositories.user.from_id(ctx, user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    rank = await repositories.leaderboard.get_star_rank(ctx, user_id)

    friend_status = FriendStatus.NONE
    friend_request = None
    messages_count = 0
    friend_request_count = 0
    friend_count = 0

    if is_own:
        messages_count = await repositories.message.from_recipient_user_id_count(
            ctx,
            user_id,
            is_new=True,
        )

        friend_request_count = (
            await repositories.friend_requests.get_user_friend_request_count(
                ctx,
                user_id,
                is_new=True,
            )
        )

        friend_count = await repositories.user_relationship.get_user_relationship_count(
            ctx,
            user_id,
            UserRelationshipType.FRIEND,
            is_new=True,
        )

    else:
        friend_check = await repositories.user_relationship.from_user_and_target_user(
            ctx,
            request_user_id,
            user_id,
            UserRelationshipType.FRIEND,
        )

        incoming_check = await repositories.friend_requests.from_target_and_recipient(
            ctx,
            user_id,
            request_user_id,
        )

        outgoing_check = await repositories.friend_requests.from_target_and_recipient(
            ctx,
            request_user_id,
            user_id,
        )

        if friend_check is not None:
            friend_status = FriendStatus.FRIEND

        elif incoming_check is not None:
            friend_status = FriendStatus.INCOMING_REQUEST
            friend_request = incoming_check

        elif outgoing_check is not None:
            friend_status = FriendStatus.OUTGOING_REQUEST
            friend_request = outgoing_check

    return UserPerspective(
        user=user,
        rank=rank,
        friend_status=friend_status,
        friend_request=friend_request,
        messages_count=messages_count,
        friend_request_count=friend_request_count,
        friend_count=friend_count,
    )


async def update_stats(
    ctx: Context,
    user_id: int,
    stars: int,
    demons: int,
    display_type: int,
    diamonds: int,
    primary_colour: int,
    secondary_colour: int,
    icon: int,
    ship: int,
    ball: int,
    ufo: int,
    wave: int,
    robot: int,
    spider: int,
    glow: bool,
    explosion: int,
    coins: int,
    user_coins: int,
    update_rank: bool = False,
) -> User | ServiceError:
    # TODO: Validation
    # TODO: Anticheat checks on the user's gains
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.USER_NOT_FOUND

    updated_user = await repositories.user.update_partial(
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
    )

    if updated_user is None:
        return ServiceError.USER_NOT_FOUND

    if update_rank:
        await repositories.leaderboard.set_star_count(ctx, user.id, updated_user.stars)

    return updated_user


async def update_user_settings(
    ctx: Context,
    user_id: int,
    message_privacy: UserPrivacySetting,
    comment_privacy: UserPrivacySetting,
    friend_privacy: UserPrivacySetting,
    youtube_name: str | None = None,
    twitter_name: str | None = None,
    twitch_name: str | None = None,
) -> User | ServiceError:
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.USER_NOT_FOUND

    updated_user = await repositories.user.update_partial(
        ctx,
        user.id,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
        message_privacy=message_privacy,
        comment_privacy=comment_privacy,
        friend_privacy=friend_privacy,
    )

    if updated_user is None:
        return ServiceError.USER_NOT_FOUND

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

    # Check if we should re-add them to the leaderboard
    elif (
        not user.privileges & UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC
    ) and privileges & UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC:
        await repositories.leaderboard.set_star_count(ctx, user_id, user.stars)

    if not privileges & UserPrivileges.USER_CP_LEADERBOARD_PUBLIC:
        # TODO: Add CP leaderboard
        ...

    updated_user = await repositories.user.update_partial(
        ctx,
        user_id,
        privileges=privileges,
    )

    if updated_user is None:
        return ServiceError.USER_NOT_FOUND

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


async def synchronise_search(ctx: Context) -> bool | ServiceError:
    users = await repositories.user.all_ids(ctx)

    for user_id in users:
        user = await repositories.user.from_id(ctx, user_id)

        if not user:
            continue

        await repositories.user.create_meili(ctx, user)

    return True


# Is the return type right?
async def search(
    ctx: Context,
    page: int,
    page_size: int,
    query: str,
) -> repositories.user.UserSearchResults | ServiceError:
    return await repositories.user.search(
        ctx,
        page,
        page_size,
        query,
    )
