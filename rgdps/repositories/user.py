from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import NamedTuple
from typing import AsyncGenerator

from rgdps.common import time as time_utils
from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
from rgdps.constants.users import DEFAULT_PRIVILEGES
from rgdps.constants.users import UserPrivacySetting
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User


async def from_db(ctx: Context, user_id: int) -> User | None:
    user_db = await ctx.mysql.fetch_one(
        "SELECT id, username, email, password, privileges, message_privacy, friend_privacy, "
        "comment_privacy, twitter_name, youtube_name, twitch_name, register_ts, "
        "stars, demons, primary_colour, secondary_colour, display_type, icon, ship, "
        "ball, ufo, wave, robot, spider, explosion, glow, creator_points, coins, "
        "user_coins, diamonds FROM users WHERE id = :id",
        {"id": user_id},
    )

    if user_db is None:
        return None

    return User.from_mapping(user_db)

async def multiple_from_db(ctx: Context, user_ids: list[int]) -> list[User]:
    users_db = await ctx.mysql.fetch_all(
        "SELECT id, username, email, password, privileges, message_privacy, friend_privacy, "
        "comment_privacy, twitter_name, youtube_name, twitch_name, register_ts, "
        "stars, demons, primary_colour, secondary_colour, display_type, icon, ship, "
        "ball, ufo, wave, robot, spider, explosion, glow, creator_points, coins, "
        "user_coins, diamonds FROM users WHERE id IN :id",
        {"ids": tuple(user_ids)},
    )

    return [User.from_mapping(user_db) for user_db in users_db]

async def create(
    ctx: Context,
    username: str,
    email: str,
    password: str,
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
    primary_colour: int = 0,
    # NOTE: secondary_colour is 4 by default in the game
    secondary_colour: int = 4,
    display_type: int = 0,
    icon: int = 0,
    ship: int = 0,
    ball: int = 0,
    ufo: int = 0,
    wave: int = 0,
    robot: int = 0,
    spider: int = 0,
    explosion: int = 0,
    glow: bool = False,
    creator_points: int = 0,
    coins: int = 0,
    user_coins: int = 0,
    diamonds: int = 0,
    user_id: int = 0,
) -> User:
    if register_ts is None:
        register_ts = datetime.now()

    user = User(
        id=user_id,
        username=username,
        email=email,
        password=password,
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
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        display_type=display_type,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        explosion=explosion,
        glow=glow,
        creator_points=creator_points,
        coins=coins,
        user_coins=user_coins,
        diamonds=diamonds,
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
        "INSERT INTO users (id, username, email, password, privileges, message_privacy, "
        "friend_privacy, comment_privacy, twitter_name, youtube_name, twitch_name, "
        "register_ts, stars, demons, primary_colour, secondary_colour, display_type, icon, "
        "ship, ball, ufo, wave, robot, spider, explosion, glow, creator_points, "
        "coins, user_coins, diamonds) VALUES (:id, :username, :email, :password, :privileges, "
        ":message_privacy, :friend_privacy, :comment_privacy, :twitter_name, :youtube_name, "
        ":twitch_name, :register_ts, :stars, :demons, :primary_colour, "
        ":secondary_colour, :display_type, :icon, :ship, :ball, :ufo, :wave, :robot, "
        ":spider, :explosion, :glow, :creator_points, :coins, :user_coins, :diamonds)",
        user.as_dict(include_id=True),
    )


async def create_meili(ctx: Context, user: User) -> None:
    user_dict = _make_meili_dict(user.as_dict(include_id=True))

    index = ctx.meili.index("users")
    await index.add_documents([user_dict])


async def update_sql_partial(
    ctx: Context,
    user_id: int,
    username: str | Unset = UNSET,
    email: str | Unset = UNSET,
    password: str | Unset = UNSET,
    privileges: UserPrivileges | Unset = UNSET,
    message_privacy: UserPrivacySetting | Unset = UNSET,
    friend_privacy: UserPrivacySetting | Unset = UNSET,
    comment_privacy: UserPrivacySetting | Unset = UNSET,
    youtube_name: str | None | Unset = UNSET,
    twitter_name: str | None | Unset = UNSET,
    twitch_name: str | None | Unset = UNSET,
    stars: int | Unset = UNSET,
    demons: int | Unset = UNSET,
    primary_colour: int | Unset = UNSET,
    secondary_colour: int | Unset = UNSET,
    display_type: int | Unset = UNSET,
    icon: int | Unset = UNSET,
    ship: int | Unset = UNSET,
    ball: int | Unset = UNSET,
    ufo: int | Unset = UNSET,
    wave: int | Unset = UNSET,
    robot: int | Unset = UNSET,
    spider: int | Unset = UNSET,
    explosion: int | Unset = UNSET,
    glow: bool | Unset = UNSET,
    creator_points: int | Unset = UNSET,
    coins: int | Unset = UNSET,
    user_coins: int | Unset = UNSET,
    diamonds: int | Unset = UNSET,
) -> User | None:
    changed_data = {}

    if is_set(username):
        changed_data["username"] = username
    if is_set(email):
        changed_data["email"] = email
    if is_set(password):
        changed_data["password"] = password
    if is_set(privileges):
        changed_data["privileges"] = privileges
    if is_set(message_privacy):
        changed_data["message_privacy"] = message_privacy.value
    if is_set(friend_privacy):
        changed_data["friend_privacy"] = friend_privacy.value
    if is_set(comment_privacy):
        changed_data["comment_privacy"] = comment_privacy.value
    if is_set(youtube_name):
        changed_data["youtube_name"] = youtube_name
    if is_set(twitter_name):
        changed_data["twitter_name"] = twitter_name
    if is_set(twitch_name):
        changed_data["twitch_name"] = twitch_name
    if is_set(stars):
        changed_data["stars"] = stars
    if is_set(demons):
        changed_data["demons"] = demons
    if is_set(primary_colour):
        changed_data["primary_colour"] = primary_colour
    if is_set(secondary_colour):
        changed_data["secondary_colour"] = secondary_colour
    if is_set(display_type):
        changed_data["display_type"] = display_type
    if is_set(icon):
        changed_data["icon"] = icon
    if is_set(ship):
        changed_data["ship"] = ship
    if is_set(ball):
        changed_data["ball"] = ball
    if is_set(ufo):
        changed_data["ufo"] = ufo
    if is_set(wave):
        changed_data["wave"] = wave
    if is_set(robot):
        changed_data["robot"] = robot
    if is_set(spider):
        changed_data["spider"] = spider
    if is_set(explosion):
        changed_data["explosion"] = explosion
    if is_set(glow):
        changed_data["glow"] = glow
    if is_set(creator_points):
        changed_data["creator_points"] = creator_points
    if is_set(coins):
        changed_data["coins"] = coins
    if is_set(user_coins):
        changed_data["user_coins"] = user_coins
    if is_set(diamonds):
        changed_data["diamonds"] = diamonds

    if not changed_data:
        return await from_id(ctx, user_id)

    query = "UPDATE users SET "
    query += ", ".join(f"{name} = :{name}" for name in changed_data.keys())
    query += " WHERE id = :id"

    changed_data["id"] = user_id

    await ctx.mysql.execute(query, changed_data)
    await drop_cache(ctx, user_id)

    return await from_id(ctx, user_id)


async def update_meili_partial(
    ctx: Context,
    user_id: int,
    username: str | Unset = UNSET,
    email: str | Unset = UNSET,
    password: str | Unset = UNSET,
    privileges: UserPrivileges | Unset = UNSET,
    message_privacy: UserPrivacySetting | Unset = UNSET,
    friend_privacy: UserPrivacySetting | Unset = UNSET,
    comment_privacy: UserPrivacySetting | Unset = UNSET,
    youtube_name: str | None | Unset = UNSET,
    twitter_name: str | None | Unset = UNSET,
    twitch_name: str | None | Unset = UNSET,
    stars: int | Unset = UNSET,
    demons: int | Unset = UNSET,
    primary_colour: int | Unset = UNSET,
    secondary_colour: int | Unset = UNSET,
    display_type: int | Unset = UNSET,
    icon: int | Unset = UNSET,
    ship: int | Unset = UNSET,
    ball: int | Unset = UNSET,
    ufo: int | Unset = UNSET,
    wave: int | Unset = UNSET,
    robot: int | Unset = UNSET,
    spider: int | Unset = UNSET,
    explosion: int | Unset = UNSET,
    glow: bool | Unset = UNSET,
    creator_points: int | Unset = UNSET,
    coins: int | Unset = UNSET,
    user_coins: int | Unset = UNSET,
    diamonds: int | Unset = UNSET,
) -> None:
    changed_data: dict[str, Any] = {
        "id": user_id,
    }

    if is_set(username):
        changed_data["username"] = username
    if is_set(email):
        changed_data["email"] = email
    if is_set(password):
        changed_data["password"] = password
    if is_set(privileges):
        changed_data["privileges"] = privileges
    if is_set(message_privacy):
        changed_data["message_privacy"] = message_privacy.value
    if is_set(friend_privacy):
        changed_data["friend_privacy"] = friend_privacy.value
    if is_set(comment_privacy):
        changed_data["comment_privacy"] = comment_privacy.value
    if is_set(youtube_name):
        changed_data["youtube_name"] = youtube_name
    if is_set(twitter_name):
        changed_data["twitter_name"] = twitter_name
    if is_set(twitch_name):
        changed_data["twitch_name"] = twitch_name
    if is_set(stars):
        changed_data["stars"] = stars
    if is_set(demons):
        changed_data["demons"] = demons
    if is_set(primary_colour):
        changed_data["primary_colour"] = primary_colour
    if is_set(secondary_colour):
        changed_data["secondary_colour"] = secondary_colour
    if is_set(display_type):
        changed_data["display_type"] = display_type
    if is_set(icon):
        changed_data["icon"] = icon
    if is_set(ship):
        changed_data["ship"] = ship
    if is_set(ball):
        changed_data["ball"] = ball
    if is_set(ufo):
        changed_data["ufo"] = ufo
    if is_set(wave):
        changed_data["wave"] = wave
    if is_set(robot):
        changed_data["robot"] = robot
    if is_set(spider):
        changed_data["spider"] = spider
    if is_set(explosion):
        changed_data["explosion"] = explosion
    if is_set(glow):
        changed_data["glow"] = glow
    if is_set(creator_points):
        changed_data["creator_points"] = creator_points
    if is_set(coins):
        changed_data["coins"] = coins
    if is_set(user_coins):
        changed_data["user_coins"] = user_coins
    if is_set(diamonds):
        changed_data["diamonds"] = diamonds

    changed_data = _make_meili_dict(changed_data)

    index = ctx.meili.index("users")
    await index.update_documents([changed_data])


async def update_partial(
    ctx: Context,
    user_id: int,
    username: str | Unset = UNSET,
    email: str | Unset = UNSET,
    password: str | Unset = UNSET,
    privileges: UserPrivileges | Unset = UNSET,
    message_privacy: UserPrivacySetting | Unset = UNSET,
    friend_privacy: UserPrivacySetting | Unset = UNSET,
    comment_privacy: UserPrivacySetting | Unset = UNSET,
    youtube_name: str | None | Unset = UNSET,
    twitter_name: str | None | Unset = UNSET,
    twitch_name: str | None | Unset = UNSET,
    stars: int | Unset = UNSET,
    demons: int | Unset = UNSET,
    primary_colour: int | Unset = UNSET,
    secondary_colour: int | Unset = UNSET,
    display_type: int | Unset = UNSET,
    icon: int | Unset = UNSET,
    ship: int | Unset = UNSET,
    ball: int | Unset = UNSET,
    ufo: int | Unset = UNSET,
    wave: int | Unset = UNSET,
    robot: int | Unset = UNSET,
    spider: int | Unset = UNSET,
    explosion: int | Unset = UNSET,
    glow: bool | Unset = UNSET,
    creator_points: int | Unset = UNSET,
    coins: int | Unset = UNSET,
    user_coins: int | Unset = UNSET,
    diamonds: int | Unset = UNSET,
) -> User | None:
    user = await update_sql_partial(
        ctx,
        user_id,
        username=username,
        email=email,
        password=password,
        privileges=privileges,
        message_privacy=message_privacy,
        friend_privacy=friend_privacy,
        comment_privacy=comment_privacy,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
        stars=stars,
        demons=demons,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        display_type=display_type,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        explosion=explosion,
        glow=glow,
        creator_points=creator_points,
        coins=coins,
        user_coins=user_coins,
        diamonds=diamonds,
    )

    if user is None:
        return None

    await update_meili_partial(
        ctx,
        user_id,
        username=username,
        email=email,
        password=password,
        privileges=privileges,
        message_privacy=message_privacy,
        friend_privacy=friend_privacy,
        comment_privacy=comment_privacy,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
        stars=stars,
        demons=demons,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        display_type=display_type,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        explosion=explosion,
        glow=glow,
        creator_points=creator_points,
        coins=coins,
        user_coins=user_coins,
        diamonds=diamonds,
    )

    await drop_cache(ctx, user_id)

    return user


async def drop_cache(ctx: Context, user_id: int) -> None:
    await ctx.user_cache.delete(user_id)

async def multiple_from_id(ctx: Context, user_ids: list[int]) -> list[User]:
    users = []
    uncached_ids = []

    for user_id in user_ids:
        cache_user = await ctx.user_cache.get(user_id)
        if cache_user is not None:
            users.append(cache_user)
        else:
            uncached_ids.append(user_id)

    db_users = await multiple_from_db(ctx, uncached_ids)
    users.extend(db_users)

    # since we fetch from cache first and db for the rest
    # users may not be in the same order they were provided in
    users.sort(key=lambda user: user_ids.index(user.id))

    return users

async def from_id(ctx: Context, user_id: int) -> User | None:
    cache_user = await ctx.user_cache.get(user_id)
    if cache_user is not None:
        return cache_user

    user = await from_db(ctx, user_id)
    if user is not None:
        await ctx.user_cache.set(user_id, user)

    return user


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
        "SELECT id, username, email, password, privileges, message_privacy, friend_privacy, "
        "comment_privacy, twitter_name, youtube_name, twitch_name, register_ts, "
        "stars, demons, primary_colour, secondary_colour, display_type, icon, ship, "
        "ball, ufo, wave, robot, spider, explosion, glow, creator_points, coins, "
        "user_coins, diamonds FROM users"
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
