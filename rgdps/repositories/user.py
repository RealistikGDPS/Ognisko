from __future__ import annotations

from typing import Optional

from rgdps import state  # TODO: Weird considering the services import.
from rgdps.config import config
from rgdps.constants.privacy import PrivacySetting
from rgdps.models.user import User
from rgdps.state import services


async def from_db(user_id: int) -> Optional[User]:
    user_db = await services.database.fetch_one(
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


async def create(user: User) -> int:
    """Inserts the user into the database, updating the user object to feature the
    new registration timestamp and ID.

    Args:
        user (User): The model of the user to insert.

    Returns:
        int: The ID of the newly inserted user.
    """

    user_id = await services.database.execute(
        "INSERT INTO users (username, email, password, privileges, message_privacy, "
        "friend_privacy, comment_privacy, twitter_name, youtube_name, twitch_name, "
        "stars, demons, primary_colour, secondary_colour, display_type, icon, "
        "ship, ball, ufo, wave, robot, spider, explosion, glow, creator_points, "
        "coins, user_coins, diamonds) VALUES (:username, :email, :password, :privileges, "
        ":message_privacy, :friend_privacy, :comment_privacy, :twitter_name, :youtube_name, "
        ":twitch_name, :stars, :demons, :primary_colour, "
        ":secondary_colour, :display_type, :icon, :ship, :ball, :ufo, :wave, :robot, "
        ":spider, :explosion, :glow, :creator_points, :coins, :user_coins, :diamonds)",
        user.as_dict(include_id=False),
    )

    return user_id


async def from_id(user_id: int) -> Optional[User]:
    cache_user = await state.repositories.user_repo.get(user_id)
    if cache_user is not None:
        return cache_user

    user = await from_db(user_id)
    if user is not None:
        await state.repositories.user_repo.set(user_id, user)

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
        user.as_dict(include_id=True),
    )

    await state.repositories.user_repo.set(user.id, user)


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
