from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class MessageDirection(str, Enum):
    # NOTE: message direction is relative to the user who is
    # making the request.
    SENT = "sent"
    RECEIVED = "received"


@dataclass
class Message:
    id: int
    sender_user_id: int
    recipient_user_id: int
    subject: str
    content: str
    post_ts: datetime
    seen_ts: datetime | None

    @staticmethod
    def from_mapping(message_dict: Mapping[str, Any]) -> Message:
        return Message(
            id=message_dict["id"],
            sender_user_id=message_dict["sender_user_id"],
            recipient_user_id=message_dict["recipient_user_id"],
            subject=message_dict["subject"],
            content=message_dict["content"],
            post_ts=message_dict["post_ts"],
            seen_ts=message_dict["seen_ts"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "sender_user_id": self.sender_user_id,
            "recipient_user_id": self.recipient_user_id,
            "subject": self.subject,
            "content": self.content,
            "post_ts": self.post_ts,
            "seen_ts": self.seen_ts,
        }

        if include_id:
            res["id"] = self.id

        return res
