from __future__ import annotations

from rgdps.common.cache.memory import SimpleAsyncMemoryCache
from rgdps.models.user import User

user_repo = SimpleAsyncMemoryCache[User]()
password_cache = SimpleAsyncMemoryCache[str]()
