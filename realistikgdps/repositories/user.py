from __future__ import annotations

from typing import Optional

from realistikgdps import state  # TODO: Weird considering the services import.
from realistikgdps.constants.privacy import PrivacySetting
from realistikgdps.models.user import User
from realistikgdps.state import services


async def from_db(user_id: int) -> Optional[User]:
    user_db = await services.database.fetch_one(
        "SELECT id, username, email, password, message_privacy, friend_privacy, "
        "comment_privacy, twitter_name, youtube_name, twitch_name, register_ts, "
        "stars, demons, primary_colour, secondary_colour, display_type, icon, ship, "
        "ball, ufo, wave, robot, spider, explosion, glow, creator_points, coins, "
        "user_coins, diamonds FROM users WHERE id = :id",
        {"id": user_id},
    )

    if user_db is None:
        return None

    return User(
        id=user_db["id"],
        username=user_db["username"],
        email=user_db["email"],
        password=user_db["password"],
        message_privacy=PrivacySetting(user_db["message_privacy"]),
        friend_privacy=PrivacySetting(user_db["friend_privacy"]),
        comment_privacy=PrivacySetting(user_db["comment_privacy"]),
        youtube_name=user_db["youtube_name"],
        twitter_name=user_db["twitter_name"],
        twitch_name=user_db["twitch_name"],
        register_ts=user_db["register_ts"],
        stars=user_db["stars"],
        demons=user_db["demons"],
        primary_colour=user_db["primary_colour"],
        secondary_colour=user_db["secondary_colour"],
        display_type=user_db["display_type"],
        icon=user_db["icon"],
        ship=user_db["ship"],
        ball=user_db["ball"],
        ufo=user_db["ufo"],
        wave=user_db["wave"],
        robot=user_db["robot"],
        spider=user_db["spider"],
        explosion=user_db["explosion"],
        glow=user_db["glow"],
        creator_points=user_db["creator_points"],
        coins=user_db["coins"],
        user_coins=user_db["user_coins"],
        diamonds=user_db["diamonds"],
    )


async def create(user: User) -> int:
    """Inserts the user into the database, updating the user object to feature the
    new registration timestamp and ID.

    Args:
        user (User): The model of the user to insert.

    Returns:
        int: The ID of the newly inserted user.
    """

    user_id = await services.database.execute(
        "INSERT INTO users (username, email, password, message_privacy, "
        "friend_privacy, comment_privacy, twitter_name, youtube_name, twitch_name, "
        "stars, demons, primary_colour, secondary_colour, display_type, icon, "
        "ship, ball, ufo, wave, robot, spider, explosion, glow, creator_points, "
        "coins, user_coins, diamonds) VALUES (:username, :email, :password, :message_privacy, "
        ":friend_privacy, :comment_privacy, :twitter_name, :youtube_name, "
        ":twitch_name, :stars, :demons, :primary_colour, "
        ":secondary_colour, :display_type, :icon, :ship, :ball, :ufo, :wave, :robot, "
        ":spider, :explosion, :glow, :creator_points, :coins, :user_coins, :diamonds)",
        {
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "message_privacy": user.message_privacy.value,
            "friend_privacy": user.friend_privacy.value,
            "comment_privacy": user.comment_privacy.value,
            "twitter_name": user.twitter_name,
            "youtube_name": user.youtube_name,
            "twitch_name": user.twitch_name,
            "stars": user.stars,
            "demons": user.demons,
            "primary_colour": user.primary_colour,
            "secondary_colour": user.secondary_colour,
            "display_type": user.display_type,
            "icon": user.icon,
            "ship": user.ship,
            "ball": user.ball,
            "ufo": user.ufo,
            "wave": user.wave,
            "robot": user.robot,
            "spider": user.spider,
            "explosion": user.explosion,
            "glow": user.glow,
            "creator_points": user.creator_points,
            "coins": user.coins,
            "user_coins": user.user_coins,
            "diamonds": user.diamonds,
        },
    )

    return user_id


async def from_id(user_id: int) -> Optional[User]:
    cache_user = state.repositories.user_repo.get(user_id)
    if cache_user is not None:
        return cache_user

    user = await from_db(user_id)
    if user is not None:
        state.repositories.user_repo[user_id] = user

    return user


async def update(user: User) -> None:
    await services.database.execute(
        "UPDATE users SET username = :username, email = :email, password = :password, "
        "message_privacy = :message_privacy, friend_privacy = :friend_privacy, "
        "comment_privacy = :comment_privacy, twitter_name = :twitter_name, "
        "youtube_name = :youtube_name, twitch_name = :twitch_name, stars = :stars, "
        "demons = :demons, primary_colour = :primary_colour, "
        "secondary_colour = :secondary_colour, display_type = :display_type, "
        "icon = :icon, ship = :ship, ball = :ball, ufo = :ufo, wave = :wave, "
        "robot = :robot, spider = :spider, explosion = :explosion, glow = :glow, "
        "creator_points = :creator_points, coins = :coins, user_coins = :user_coins, "
        "diamonds = :diamonds WHERE id = :id",
        {
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "message_privacy": user.message_privacy.value,
            "friend_privacy": user.friend_privacy.value,
            "comment_privacy": user.comment_privacy.value,
            "twitter_name": user.twitter_name,
            "youtube_name": user.youtube_name,
            "twitch_name": user.twitch_name,
            "stars": user.stars,
            "demons": user.demons,
            "primary_colour": user.primary_colour,
            "secondary_colour": user.secondary_colour,
            "display_type": user.display_type,
            "icon": user.icon,
            "ship": user.ship,
            "ball": user.ball,
            "ufo": user.ufo,
            "wave": user.wave,
            "robot": user.robot,
            "spider": user.spider,
            "explosion": user.explosion,
            "glow": user.glow,
            "creator_points": user.creator_points,
            "coins": user.coins,
            "user_coins": user.user_coins,
            "id": user.id,
            "diamonds": user.diamonds,
        },
    )


async def check_email_exists(email: str) -> bool:
    return await services.database.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = :email)",
        {
            "email": email,
        },
    )


async def check_username_exists(username: str) -> bool:
    return await services.database.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM users WHERE username = :username)",
        {
            "username": username,
        },
    )


async def from_name(username: str) -> Optional[User]:
    user_id = await services.database.fetch_val(
        "SELECT id FROM users WHERE username = :username",
        {
            "username": username,
        },
    )

    if user_id is None:
        return None

    return await from_id(user_id)
