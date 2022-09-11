# Usecases for users and accounts (as they usually heavily overlap).
from __future__ import annotations

import logging
from typing import NamedTuple
from typing import Optional

import realistikgdps.repositories
import realistikgdps.state
from realistikgdps.models.account import Account
from realistikgdps.models.user import User


class UserAccount(NamedTuple):
    user: User
    account: Account


async def from_id(account_id: int) -> Optional[UserAccount]:
    account = await realistikgdps.repositories.account.from_id(account_id)

    if account is None:
        return None

    user = await realistikgdps.repositories.user.from_id(account.user_id)

    if user is None:
        logging.warning(
            f"The account {account} has no user associated with it. "
            "This should NEVER happen.",
        )
        return None

    return UserAccount(user=user, account=account)


async def register(name: str, password: str, email: str) -> UserAccount:
    account = Account(
        id=0,
        user_id=0,
        name=name,
        password=password,
        email=email,
        messages_blocked=False,
        friend_req_blocked=False,
        comment_history_hidden=False,
        youtube_name=None,
        twitter_name=None,
        twitch_name=None,
    )

    account_id = await realistikgdps.repositories.account.into_db(account)

    user = User(
        id=0,
        ext_id=str(account_id),
        name=name,
        stars=0,
        demons=0,
        primary_colour=0,
        secondary_colour=0,
        display_type=0,
        coins=0,
        user_coins=0,
        creator_points=0,
        icon=0,
        ship=0,
        ball=0,
        ufo=0,
        wave=0,
        robot=0,
        spider=0,
        glow=False,
        player_lb_ban=False,
        creator_lb_ban=False,
    )

    user_id = await realistikgdps.repositories.user.into_db(user)

    # Update the account with the new user ID
    account.user_id = user_id
    await realistikgdps.repositories.account.update(account)

    return UserAccount(user=user, account=account)


async def account_from_name(name: str) -> Optional[Account]:
    # Iterate over the cached accounts in case its in there
    for account in realistikgdps.state.repositories.account_repo.values():
        if account.name == name:
            return account

    # Query the database for their account ID.
    account_id = await realistikgdps.state.services.database.fetch_val(
        "SELECT accountID FROM accounts WHERE userName = :name LIMIT 1",  # TODO: Maybe use LIKE instead?
        {
            "name": name,
        },
    )

    if account_id is None:
        return None

    return await realistikgdps.repositories.account.from_id(account_id)


async def user_from_name(name: str) -> Optional[User]:
    # Iterate over the cached users in case its in there
    for user in realistikgdps.state.repositories.user_repo.values():
        if user.name == name:
            return user

    # Query the database for their user ID.
    user_id = await realistikgdps.state.services.database.fetch_val(
        "SELECT userID FROM users WHERE userName = :name LIMIT 1",  # TODO: Maybe use LIKE instead?
        {
            "name": name,
        },
    )

    if user_id is None:
        return None

    return await realistikgdps.repositories.user.from_id(user_id)
