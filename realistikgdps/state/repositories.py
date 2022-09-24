from __future__ import annotations

from realistikgdps.models.user import User

user_repo: dict[int, User] = {}
password_cache: dict[str, str] = {}  # hash: known_password
