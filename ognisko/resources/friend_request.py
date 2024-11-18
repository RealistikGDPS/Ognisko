from __future__ import annotations

from datetime import datetime

from ognisko.adapters import AbstractMySQLService
from ognisko.common import modelling
from ognisko.resources._common import DatabaseModel

class FriendRequest(DatabaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    message: str
    post_ts: datetime
    seen_ts: datetime | None
