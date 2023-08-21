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
    def from_mapping(friend_request_dict: Mapping[str, Any]) -> FriendRequest:
        return FriendRequest(
            id=friend_request_dict["id"],
            sender_user_id=friend_request_dict["sender_user_id"],
            recipient_user_id=friend_request_dict["recipient_user_id"],
            message=friend_request_dict["message"],
            post_ts=friend_request_dict["post_ts"],
            seen_ts=friend_request_dict["seen_ts"],
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
