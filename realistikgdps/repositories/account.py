from __future__ import annotations

from typing import Optional

import realistikgdps.state
from realistikgdps.models.account import Account


async def from_db(account_id: int) -> Optional[Account]:
    acc_db = await realistikgdps.state.services.database.fetch_one(
        "SELECT accountID, userName, password, email, mS, frS, cS, userID, "
        "youtubeurl, twitter, twitch FROM accounts WHERE accountID = :account_id",
        {
            "account_id": account_id,
        },
    )

    if acc_db is None:
        return None

    return Account(
        id=acc_db["accountID"],
        name=acc_db["userName"],
        password=acc_db["password"],
        email=acc_db["email"],
        messages_blocked=acc_db["mS"] == 1,
        friend_req_blocked=acc_db["frS"] == 1,
        comment_history_hidden=acc_db["cS"] == 1,
        youtube_name=acc_db["youtubeurl"],
        twitter_name=acc_db["twitter"],
        twitch_name=acc_db["twitch"],
        user_id=acc_db["userID"],
    )


async def create(account: Account) -> int:
    return await realistikgdps.state.services.database.execute(
        "INSERT INTO accounts (userName, password, email, mS, frS, cS, "
        "youtubeurl, twitter, twitch, userID) VALUES (:name, :password, :email, :messages_blocked, "
        ":friend_req_blocked, :comment_history_hidden, :youtube_name, :twitter_name, "
        ":twitch_name, :user_id)",
        {
            "name": account.name,
            "password": account.password,
            "email": account.email,
            "messages_blocked": account.messages_blocked,
            "friend_req_blocked": account.friend_req_blocked,
            "comment_history_hidden": account.comment_history_hidden,
            "youtube_name": account.youtube_name,
            "twitter_name": account.twitter_name,
            "twitch_name": account.twitch_name,
            "user_id": account.user_id,
        },
    )


def into_cache(account: Account) -> None:
    realistikgdps.state.repositories.account_repo[account.id] = account


def from_cache(account_id: int) -> Optional[Account]:
    return realistikgdps.state.repositories.account_repo.get(account_id)


async def from_id(account_id: int) -> Optional[Account]:
    """Attempts to fetch an account from multiple sources ordered by speed.

    Args:
        account_id (int): The ID of the account to fetch.

    Returns:
        Optional[Account]: The account if it exists, otherwise None.
    """

    if account := from_cache(account_id):
        return account

    if account := await from_db(account_id):
        into_cache(account)
        return account

    return None


async def update(account: Account) -> None:
    await realistikgdps.state.services.database.execute(
        "UPDATE accounts SET userName = :name, password = :password, email = :email, "
        "mS = :messages_blocked, frS = :friend_req_blocked, cS = :comment_history_hidden, "
        "youtubeurl = :youtube_name, twitter = :twitter_name, twitch = :twitch_name, "
        "userID = :user_id WHERE accountID = :account_id",
        {
            "name": account.name,
            "password": account.password,
            "email": account.email,
            "messages_blocked": account.messages_blocked,
            "friend_req_blocked": account.friend_req_blocked,
            "comment_history_hidden": account.comment_history_hidden,
            "youtube_name": account.youtube_name,
            "twitter_name": account.twitter_name,
            "twitch_name": account.twitch_name,
            "user_id": account.user_id,
            "account_id": account.id,
        },
    )


async def from_name(name: str) -> Optional[Account]:
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

    return await from_id(account_id)
