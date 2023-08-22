from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping


@dataclass
class FriendRequest:
    id: int
    sender_user_id: int
    recipient_user_id: int
    message: str
    post_ts: datetime
    seen_ts: datetime | None

    @staticmethod
    def from_mapping(mapping: Mapping[str, Any]) -> FriendRequest:
        return FriendRequest(
            id=mapping["id"],
            sender_user_id=mapping["sender_user_id"],
            recipient_user_id=mapping["recipient_user_id"],
            message=mapping["message"],
            post_ts=mapping["post_ts"],
            seen_ts=mapping["seen_ts"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "sender_user_id": self.sender_user_id,
            "recipient_user_id": self.recipient_user_id,
            "message": self.message,
            "post_ts": self.post_ts,
            "seen_ts": self.seen_ts,
        }

        if include_id:
            res["id"] = self.id

        return res
