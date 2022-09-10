from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from realistikgdps.models.user import User

USER_REPO: dict[int, User] = {}
