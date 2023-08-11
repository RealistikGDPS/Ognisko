#!/usr/bin/env python3.10
from __future__ import annotations

import sys

# This is a hack to allow the script to be run from the root directory.
sys.path.append(".")

# The database converter for the GMDPS database.
# Please see the README for more information.
import asyncio
import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote
from urllib.parse import unquote
import traceback

import httpx
from databases import DatabaseURL
from meilisearch_python_async import Client as MeiliClient
from redis.asyncio import Redis
from types_aiobotocore_s3 import S3Client

from rgdps import logger
from rgdps import repositories
from rgdps.common.cache.memory import SimpleAsyncMemoryCache
from rgdps.common.context import Context
from rgdps.common.time import from_unix_ts
from rgdps.common import hashes
from rgdps.config import config
from rgdps.constants.levels import LevelDemonDifficulty
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.users import UserPrivacySetting
from rgdps.constants.users import UserPrivileges
from rgdps.constants.songs import SongSource
from rgdps.services.mysql import MySQLService
from rgdps.models.user import User

if TYPE_CHECKING:
    from rgdps.common.cache.base import AbstractAsyncCache


# TODO: Customisable (without affecting the actual config)
OLD_DB = "old_rgdps"
OLD_DB_USER = "root"

# Matches CVGDPS defaults.
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


@dataclass
class ConverterContext(Context):
    _mysql: MySQLService
    _redis: Redis
    _meili: MeiliClient
    _user_cache: AbstractAsyncCache[User]
    _password_cache: AbstractAsyncCache[str]
    _http: httpx.AsyncClient
    old_sql: MySQLService
    user_id_map: dict[int, int]

    @property
    def mysql(self) -> MySQLService:
        return self._mysql

    @property
    def redis(self) -> Redis:
        return self._redis

    @property
    def meili(self) -> MeiliClient:
        return self._meili

    @property
    def s3(self) -> S3Client | None:
        # We are not using storage.
        return None

    @property
    def user_cache(self) -> AbstractAsyncCache[User]:
        return self._user_cache

    @property
    def password_cache(self) -> AbstractAsyncCache[str]:
        return self._password_cache

    @property
    def http(self) -> httpx.AsyncClient:
        return self._http


async def create_user_id_map(conn: MySQLService) -> dict[int, int]:
    """Creates a UserID -> AccountID map (separate concepts in GMDPS)."""

    res = await conn.fetch_all(
        "SELECT u.userID, a.accountID FROM users u INNER JOIN accounts a "
        "ON u.extID = a.accountID WHERE isRegistered = 1",
    )

    return {row["userID"]: row["accountID"] for row in res}


async def create_role_map(conn: MySQLService) -> dict[int, dict]:
    """Creates a RoleID -> Role map."""

    res = await conn.fetch_all(
        "SELECT * FROM roles",
    )

    return {row["roleID"]: row for row in res}  # type: ignore


async def create_role_assign_map(conn: MySQLService) -> dict[int, int]:
    """Creates a RoleID -> AccountID map."""

    res = await conn.fetch_all(
        "SELECT * FROM roleassign",
    )

    return {row["accountID"]: row["roleID"] for row in res}


async def get_context() -> ConverterContext:
    database_url = DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=config.sql_user,
            password=quote(config.sql_pass),
            host=config.sql_host,
            port=config.sql_port,
            db=config.sql_db,
        ),
    )

    mysql = MySQLService(database_url)
    await mysql.connect()

    old_database_url = DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=OLD_DB_USER,
            password=quote(config.sql_pass),
            host=config.sql_host,
            port=config.sql_port,
            db=OLD_DB,
        ),
    )

    old_sql = MySQLService(old_database_url)
    await old_sql.connect()

    redis = Redis.from_url(
        f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    )
    await redis.initialize()

    meili = MeiliClient(
        f"http://{config.meili_host}:{config.meili_port}",
        config.meili_key,
        timeout=10,
    )
    await meili.health()

    user_cache = SimpleAsyncMemoryCache[User]()
    password_cache = SimpleAsyncMemoryCache[str]()
    http = httpx.AsyncClient()

    user_id_map = await create_user_id_map(old_sql)

    return ConverterContext(
        mysql,
        redis,
        meili,
        user_cache,
        password_cache,
        http,
        old_sql,
        user_id_map,
    )


async def convert_songs(ctx: ConverterContext) -> None:
    old_songs = await ctx.old_sql.fetch_all(
        "SELECT * FROM songs",
    )

    for song in old_songs:
        # GMDPS stores the download URL as a URL-encoded string.
        download_url = unquote(song["download"])
        # GMDPS lets reuploaded songs bypass the name limit?
        song_name = song["name"][:32]
        # Size is varchar(100)....
        try:
            size = float(song["size"])
        except ValueError:
            logger.warning(f"Song {song_name} (ID {song['ID']}) has an invalid size.")
            size = 0.0

        if "ngfiles" in download_url:
            source = SongSource.BOOMLINGS
        else:
            source = SongSource.CUSTOM

        if len(download_url) > 256:
            logger.warning(
                f"Skipping song {song_name} (ID {song['ID']}) because the "
                "download URL is too long.",
            )
            continue

        await repositories.song.create(
            ctx,
            song_id=song["ID"],
            name=song_name,
            author_id=song["authorID"],
            author=song["authorName"],
            download_url=download_url,
            size=size,
            blocked=song["isDisabled"] > 0,
            source=source,
        )


async def convert_user_comments(ctx: ConverterContext) -> None:
    old_comments = await ctx.old_sql.fetch_all(
        "SELECT * FROM acccomments",
    )

    for comment in old_comments:
        account_id = ctx.user_id_map.get(comment["userID"])
        if account_id is None:
            logger.warning(
                f"Failed to find account ID for user ID {comment['userID']}.",
            )
            continue

        post_ts = from_unix_ts(comment["timestamp"])
        content = hashes.decode_base64(comment["comment"])[:256]

        await repositories.user_comment.create(
            ctx,
            comment_id=comment["commentID"],
            user_id=account_id,
            content=content,
            likes=comment["likes"],
            post_ts=post_ts,
        )


async def convert_level_comments(ctx: ConverterContext) -> None:
    old_comments = await ctx.old_sql.fetch_all(
        "SELECT * FROM comments",
    )

    for comment in old_comments:
        account_id = ctx.user_id_map.get(comment["userID"])
        if account_id is None:
            logger.warning(
                f"Failed to find account ID for user ID {comment['userID']}.",
            )
            continue

        post_ts = from_unix_ts(comment["timestamp"])
        content = hashes.decode_base64(comment["comment"])[:256]

        await repositories.level_comment.create(
            ctx,
            comment_id=comment["commentID"],
            user_id=account_id,
            content=content,
            likes=comment["likes"],
            post_ts=post_ts,
            percent=comment["percent"],
            level_id=comment["levelID"],
        )


async def convert_users(ctx: ConverterContext) -> None:
    # Why.
    old_users = await ctx.old_sql.fetch_all(
        "SELECT a.accountID, a.username, a.password, a.email, a.userID, a.mS, a.frS, a.cS, a.youtubeurl, a.twitter, "
        "a.twitch, a.registerDate, u.stars, u.demons, u.icon, u.color1, u.color2, u.iconType, u.coins, u.userCoins, "
        "u.accShip, u.accBall, u.accBird, u.accDart, u.accRobot, u.accGlow, u.accSpider, u.accExplosion, "
        "u.creatorPoints, u.diamonds, u.isBanned "
        "FROM accounts a INNER JOIN users u ON a.accountID = u.extID WHERE isRegistered = 1",
    )

    roles = await create_role_map(ctx.old_sql)
    role_assign = await create_role_assign_map(ctx.old_sql)

    for user in old_users:
        user_id = user["accountID"]
        # Privilege conversion
        privileges = DEFAULT_PRIVILEGES

        if user["isBanned"]:
            privileges &= ~UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC

        if (role_id := role_assign.get(user_id)) and (role := roles.get(role_id)):
            # Mod badge
            if role["modBadgeLevel"] == 2:
                privileges |= UserPrivileges.USER_DISPLAY_ELDER_BADGE
            elif role["modBadgeLevel"] == 1:
                privileges |= UserPrivileges.USER_DISPLAY_MOD_BADGE

            if role["actionRateStars"]:
                privileges |= UserPrivileges.LEVEL_RATE_STARS

            if role["actionRequestMod"] == 2:
                privileges |= UserPrivileges.USER_REQUEST_ELDER
            elif role["actionRequestMod"] == 1:
                privileges |= UserPrivileges.USER_REQUEST_MODERATOR

        # CBA with data out of range errors.
        try:
            await repositories.user.create(
                ctx,
                user_id=user_id,
                username=user["username"],
                password=user["password"],
                email=user["email"],
                privileges=privileges,
                message_privacy=UserPrivacySetting(user["mS"]),
                friend_privacy=UserPrivacySetting(user["frS"]),
                comment_privacy=UserPrivacySetting(user["cS"]),
                youtube_name=user["youtubeurl"][:25],
                twitter_name=user["twitter"][:15],
                twitch_name=user["twitch"][:25],
                register_ts=from_unix_ts(user["registerDate"]),
                stars=user["stars"],
                demons=user["demons"],
                primary_colour=user["color1"],
                secondary_colour=user["color2"],
                display_type=user["iconType"],
                icon=user["icon"],
                ship=user["accShip"],
                ball=user["accBall"],
                ufo=user["accBird"],
                wave=user["accDart"],
                robot=user["accRobot"],
                spider=user["accSpider"],
                explosion=user["accExplosion"],
                glow=user["accGlow"],
                creator_points=user["creatorPoints"],
                coins=user["coins"],
                user_coins=user["userCoins"],
                diamonds=user["diamonds"],
            )
        except Exception:
            logger.error(f"Failed to convert user {user_id}\n" + traceback.format_exc())


async def convert_levels(ctx: ConverterContext) -> None:
    old_levels = await ctx.old_sql.fetch_all(
        "SELECT * FROM levels",
    )

    for level in old_levels:
        account_id = ctx.user_id_map.get(level["userID"])
        # Rip unregistered users' levels
        if account_id is None:
            continue

        description = hashes.decode_base64(level["levelDesc"])[:256]

        publicity = LevelPublicity.PUBLIC
        if level["unlisted"] > 0:
            publicity = LevelPublicity.GLOBAL_UNLISTED

        demon_difficulty = None
        if level["starDemonDiff"] > 0:
            demon_difficulty = LevelDemonDifficulty(level["starDemonDiff"])

        search_flag = LevelSearchFlag.NONE

        if level["starEpic"] > 0:
            search_flag |= LevelSearchFlag.EPIC

        if not level["songID"]:
            custom_song_id = None
            official_song_id = level["audioTrack"]
        else:
            custom_song_id = level["songID"]
            official_song_id = None

        await repositories.level.create(
            ctx,
            level_id=level["levelID"],
            name=level["levelName"][:32],
            user_id=account_id,
            description=description,
            version=level["levelVersion"],
            length=LevelLength(level["levelLength"]),
            official_song_id=official_song_id,
            custom_song_id=custom_song_id,
            copy_password=level["password"],
            original_id=level["original"],
            two_player=level["twoPlayer"] > 0,
            object_count=abs(level["objects"]),
            coins=level["coins"],
            requested_stars=level["requestedStars"],
            render_str=level["extraString"],
            difficulty=LevelDifficulty(level["starDifficulty"]),
            downloads=level["downloads"],
            likes=level["likes"],
            stars=level["starStars"],
            # NOTE: Only upload ts is varchar.
            upload_ts=from_unix_ts(int(level["uploadDate"])),
            update_ts=from_unix_ts(level["updateDate"]),
            coins_verified=level["starCoins"] > 0,
            feature_order=level["starFeatured"],
            deleted=level["isDeleted"] > 0,
            low_detail_mode=level["isLDM"] > 0,
            publicity=publicity,
            demon_difficulty=demon_difficulty,
            search_flags=search_flag,
        )


async def main() -> int:
    logger.info("Starting the GMDPS -> RealistikGDPS converter.")
    ctx = await get_context()

    logger.info("Successfully connected!")

    try:
        if not await repositories.song.get_count(ctx):
            logger.info("Converting songs...")
            await convert_songs(ctx)
        else:
            logger.info("Skipping song conversion, songs already exist.")

        if not await repositories.user.get_count(ctx):
            logger.info("Converting users...")
            await convert_users(ctx)
        else:
            logger.info("Skipping user conversion, users already exist.")

        if not await repositories.level.get_count(ctx):
            logger.info("Converting levels...")
            await convert_levels(ctx)
        else:
            logger.info("Skipping level conversion, levels already exist.")

        if not await repositories.user_comment.get_count(ctx):
            logger.info("Converting user comments...")
            await convert_user_comments(ctx)
        else:
            logger.info(
                "Skipping user comment conversion, user comments already exist.",
            )

        if not await repositories.level_comment.get_count(ctx):
            logger.info("Converting level comments...")
            await convert_level_comments(ctx)
        else:
            logger.info(
                "Skipping level comment conversion, level comments already exist.",
            )
    except Exception:
        logger.error(
            "Failed to convert data with exception:\n" + traceback.format_exc(),
        )

    logger.info("Migration complete!")
    # TODO: Look into a better approach to stop docker
    # from restarting the container.
    while True:
        await asyncio.sleep(100)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
