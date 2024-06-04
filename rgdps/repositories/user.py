from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from typing import NamedTuple
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from rgdps.common import modelling
from rgdps.common import time as time_utils
from rgdps.common.context import Context
from rgdps.constants.users import DEFAULT_PRIVILEGES
from rgdps.constants.users import UserPrivacySetting
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User

ALL_FIELDS = modelling.get_model_fields(User)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


async def from_db(ctx: Context, user_id: int) -> User | None:
    user_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM users WHERE id = :id",
        {"id": user_id},
    )

    if user_db is None:
        return None

    return User.from_mapping(user_db)


async def multiple_from_db(ctx: Context, user_ids: list[int]) -> list[User]:
    if not user_ids:
        return []

    users_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM users WHERE id IN :ids",
        {"ids": tuple(user_ids)},
    )

    return [User.from_mapping(user_db) for user_db in users_db]


async def create(
    ctx: Context,
    username: str,
    email: str,
    privileges: UserPrivileges = DEFAULT_PRIVILEGES,
    message_privacy: UserPrivacySetting = UserPrivacySetting.PUBLIC,
    friend_privacy: UserPrivacySetting = UserPrivacySetting.PUBLIC,
    comment_privacy: UserPrivacySetting = UserPrivacySetting.PUBLIC,
    youtube_name: str | None = None,
    twitter_name: str | None = None,
    twitch_name: str | None = None,
    register_ts: datetime | None = None,
    stars: int = 0,
    demons: int = 0,
    moons: int = 0,
    primary_colour: int = 0,
    # NOTE: secondary_colour is 4 by default in the game
    secondary_colour: int = 4,
    glow_colour: int = 0,
    display_type: int = 0,
    icon: int = 0,
    ship: int = 0,
    ball: int = 0,
    ufo: int = 0,
    wave: int = 0,
    robot: int = 0,
    spider: int = 0,
    swing_copter: int = 0,
    jetpack: int = 0,
    explosion: int = 0,
    glow: bool = False,
    creator_points: int = 0,
    coins: int = 0,
    user_coins: int = 0,
    diamonds: int = 0,
    user_id: int = 0,
    comment_colour: str = "0,0,0",
) -> User:
    if register_ts is None:
        register_ts = datetime.now()

    user = User(
        id=user_id,
        username=username,
        email=email,
        privileges=privileges,
        message_privacy=message_privacy,
        friend_privacy=friend_privacy,
        comment_privacy=comment_privacy,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
        register_ts=register_ts,
        stars=stars,
        demons=demons,
        moons=moons,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        glow_colour=glow_colour,
        display_type=display_type,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        swing_copter=swing_copter,
        jetpack=jetpack,
        explosion=explosion,
        glow=glow,
        creator_points=creator_points,
        coins=coins,
        user_coins=user_coins,
        diamonds=diamonds,
        comment_colour=comment_colour,
    )

    user.id = await create_sql(ctx, user)
    await create_meili(ctx, user)

    return user


def _make_meili_dict(user_dict: dict[str, Any]) -> dict[str, Any]:
    user_dict = user_dict.copy()

    if "privileges" in user_dict:
        user_dict["privileges"] = int.from_bytes(
            user_dict["privileges"],
            byteorder="little",
            signed=False,
        )
        user_dict["is_public"] = (
            user_dict["privileges"] & UserPrivileges.USER_PROFILE_PUBLIC > 0
        )

    if "register_ts" in user_dict:
        user_dict["register_ts"] = time_utils.into_unix_ts(user_dict["register_ts"])

    return user_dict


def _from_meili_dict(user_dict: dict[str, Any]) -> dict[str, Any]:
    user_dict = user_dict.copy()

    user_dict["privileges"] = UserPrivileges(int(user_dict["privileges"])).as_bytes()

    user_dict["register_ts"] = time_utils.from_unix_ts(user_dict["register_ts"])

    del user_dict["is_public"]

    return user_dict


async def create_sql(ctx: Context, user: User) -> int:
    return await ctx.mysql.execute(
        f"INSERT INTO users ({_ALL_FIELDS_COMMA}) VALUES ({_ALL_FIELDS_COLON})",
        user.as_dict(include_id=True),
    )


async def create_meili(ctx: Context, user: User) -> None:
    user_dict = _make_meili_dict(user.as_dict(include_id=True))

    index = ctx.meili.index("users")
    await index.add_documents([user_dict])


class _UserUpdatePartial(TypedDict):
    username: NotRequired[str]
    email: NotRequired[str]
    privileges: NotRequired[UserPrivileges]
    message_privacy: NotRequired[UserPrivacySetting]
    friend_privacy: NotRequired[UserPrivacySetting]
    comment_privacy: NotRequired[UserPrivacySetting]
    youtube_name: NotRequired[str | None]
    twitter_name: NotRequired[str | None]
    twitch_name: NotRequired[str | None]
    stars: NotRequired[int]
    demons: NotRequired[int]
    moons: NotRequired[int]
    primary_colour: NotRequired[int]
    secondary_colour: NotRequired[int]
    glow_colour: NotRequired[int]
    display_type: NotRequired[int]
    icon: NotRequired[int]
    ship: NotRequired[int]
    ball: NotRequired[int]
    ufo: NotRequired[int]
    wave: NotRequired[int]
    robot: NotRequired[int]
    spider: NotRequired[int]
    swing_copter: NotRequired[int]
    jetpack: NotRequired[int]
    explosion: NotRequired[int]
    glow: NotRequired[bool]
    creator_points: NotRequired[int]
    coins: NotRequired[int]
    user_coins: NotRequired[int]
    diamonds: NotRequired[int]
    comment_colour: NotRequired[str]


async def update_sql_partial(
    ctx: Context,
    user_id: int,
    **kwargs: Unpack[_UserUpdatePartial],
) -> User | None:
    changed_fields = modelling.unpack_enum_types(kwargs)

    await ctx.mysql.execute(
        modelling.update_from_partial_dict("users", user_id, changed_fields),
        changed_fields,
    )

    return await from_id(ctx, user_id)


async def update_meili_partial(
    ctx: Context,
    user_id: int,
    **kwargs: Unpack[_UserUpdatePartial],
) -> None:
    changed_data = modelling.unpack_enum_types(kwargs)
    changed_data["id"] = user_id
    changed_data = _make_meili_dict(changed_data)

    index = ctx.meili.index("users")
    await index.update_documents([changed_data])


async def update_partial(
    ctx: Context,
    user_id: int,
    **kwargs: Unpack[_UserUpdatePartial],
) -> User | None:
    user = await update_sql_partial(ctx, user_id, **kwargs)

    if user is None:
        return None

    await update_meili_partial(ctx, user_id, **kwargs)

    return user



async def multiple_from_id(ctx: Context, user_ids: list[int]) -> list[User]:
    if not user_ids:
        return []

    db_users = await multiple_from_db(ctx, user_ids)
    return db_users


async def from_id(ctx: Context, user_id: int) -> User | None:
    return await from_db(ctx, user_id)


async def check_email_exists(ctx: Context, email: str) -> bool:
    return await ctx.mysql.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = :email)",
        {
            "email": email,
        },
    )


async def check_username_exists(ctx: Context, username: str) -> bool:
    return await ctx.mysql.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM users WHERE username = :username)",
        {
            "username": username,
        },
    )


async def from_name(ctx: Context, username: str) -> User | None:
    user_id = await ctx.mysql.fetch_val(
        "SELECT id FROM users WHERE username = :username",
        {
            "username": username,
        },
    )

    if user_id is None:
        return None

    return await from_id(ctx, user_id)


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM users")


async def all(ctx: Context) -> AsyncGenerator[User, None]:
    async for db_user in ctx.mysql.iterate(
        f"SELECT {_ALL_FIELDS_COMMA} FROM users",
    ):
        yield User.from_mapping(db_user)


class UserSearchResults(NamedTuple):
    results: list[User]
    total: int


async def search(
    ctx: Context,
    page: int,
    page_size: int,
    query: str,
    include_hidden: bool = False,
) -> UserSearchResults:
    index = ctx.meili.index("users")

    filters = []
    if not include_hidden:
        filters.append("is_public = true")

    results_db = await index.search(
        query,
        offset=page * page_size,
        limit=page_size,
        filter=filters,
    )

    if (not results_db.hits) or (not results_db.estimated_total_hits):
        return UserSearchResults([], 0)

    results = [
        User.from_mapping(_from_meili_dict(result)) for result in results_db.hits
    ]

    return UserSearchResults(results, results_db.estimated_total_hits)
