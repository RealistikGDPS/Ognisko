from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from realistikgdps.models.user import User
    from realistikgdps.models.account import Account

user_repo: dict[int, User] = {}
ACCOUNT_REPO: dict[int, Account] = {}
