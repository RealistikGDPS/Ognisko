# Usecases for users and accounts (as they usually heavily overlap).
from __future__ import annotations

from typing import Any
from typing import NamedTuple
from typing import Optional

import realistikgdps.repositories
import realistikgdps.state
from realistikgdps import logger
from realistikgdps.constants.privacy import PrivacySetting
from realistikgdps.models.account import Account
from realistikgdps.models.user import User
from realistikgdps.typing.types import GDSerialisable


class UserAccount(NamedTuple):
    user: User
    account: Account


async def from_id(account_id: int) -> Optional[UserAccount]:
    account = await realistikgdps.repositories.account.from_id(account_id)

    if account is None:
        return None

    user = await realistikgdps.repositories.user.from_id(account.user_id)

    if user is None:
        logger.warning(
            f"The account {account} has no user associated with it. "
            "This should NEVER happen.",
            account=account,
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
        messages=PrivacySetting.PUBLIC,
        friend_requests=PrivacySetting.PUBLIC,
        comment_history=PrivacySetting.PUBLIC,
        youtube_name=None,
        twitter_name=None,
        twitch_name=None,
    )

    account_id = await realistikgdps.repositories.account.create(account)

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
        explosion=0,
    )

    user_id = await realistikgdps.repositories.user.create(user)

    # Update the account with the new user ID
    account.user_id = user_id
    await realistikgdps.repositories.account.update(account)

    return UserAccount(user=user, account=account)


def create_gd_profile_object(user_account: UserAccount) -> GDSerialisable:
    return {
        1: user_account.account.name,
        2: user_account.user.id,
        3: user_account.user.stars,
        4: user_account.user.demons,
        6: 0,  # TODO: Implement rank
        7: user_account.account.id,
        8: user_account.user.creator_points,
        9: user_account.user.display_type,
        10: user_account.user.primary_colour,
        11: user_account.user.secondary_colour,
        13: user_account.user.coins,
        14: user_account.user.icon,
        15: 0,
        16: user_account.account.id,
        17: user_account.user.user_coins,
        18: user_account.account.messages.value,
        19: user_account.account.friend_requests.value,
        20: user_account.account.youtube_name or "",
        21: user_account.user.icon,
        22: user_account.user.ship,
        23: user_account.user.ball,
        24: user_account.user.ufo,
        25: user_account.user.wave,
        26: user_account.user.robot,
        28: int(user_account.user.glow),
        29: 1,  # Is Registered
        30: 0,  # TODO: Implement rank
        31: 0,  # Friend state (should be handled on case basis)
        43: user_account.user.spider,
        44: user_account.account.twitter_name or "",
        45: user_account.account.twitch_name or "",
        46: 0,  # TODO: Diamonds, which require save data parsing....
        48: user_account.user.explosion,
        49: 0,  # TODO: Badge level with privileges.
        50: user_account.account.comment_history.value,
    }
