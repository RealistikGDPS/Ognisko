from __future__ import annotations

from typing import Optional

from rgdps.common.context import Context
from rgdps.config import config
from rgdps.constants.privacy import PrivacySetting
from rgdps.models.user import User


async def from_db(ctx: Context, user_id: int) -> Optional[User]:
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


async def create(ctx: Context, user: User) -> int:
    """Inserts the user into the database, updating the user object to feature the
    new registration timestamp and ID.

    Args:
        user (User): The model of the user to insert.

    Returns:
        int: The ID of the newly inserted user.
    """

    user_id = await ctx.mysql.execute(
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


async def from_id(ctx: Context, user_id: int) -> Optional[User]:
    cache_user = await ctx.user_cache.get(user_id)
    if cache_user is not None:
        return cache_user

    user = await from_db(ctx, user_id)
    if user is not None:
        await ctx.user_cache.set(user_id, user)

    return user


async def update(ctx: Context, user: User) -> None:
    await ctx.mysql.execute(
        "UPDATE users SET username = :username, email = :email, password = :password, "
        "message_privacy = :message_privacy, friend_privacy = :friend_privacy, "
        "comment_privacy = :comment_privacy, twitter_name = :twitter_name, "
        "youtube_name = :youtube_name, twitch_name = :twitch_name, stars = :stars, "
        "demons = :demons, primary_colour = :primary_colour, "
        "secondary_colour = :secondary_colour, display_type = :display_type, "
        "icon = :icon, ship = :ship, ball = :ball, ufo = :ufo, wave = :wave, "
        "robot = :robot, spider = :spider, explosion = :explosion, glow = :glow, "
        "creator_points = :creator_points, coins = :coins, user_coins = :user_coins, "
        "diamonds = :diamonds, privileges = :privileges WHERE id = :id",
        user.as_dict(include_id=True),
    )

    await ctx.user_cache.set(user.id, user)


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


async def from_name(ctx: Context, username: str) -> Optional[User]:
    user_id = await ctx.mysql.fetch_val(
        "SELECT id FROM users WHERE username = :username",
        {
            "username": username,
        },
    )

    if user_id is None:
        return None

    return await from_id(ctx, user_id)
