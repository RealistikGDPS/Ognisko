from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping


@dataclass
class UserComment:
    id: int
    user_id: int
    content: str
    likes: int
    post_ts: datetime
    deleted: bool

    @staticmethod
    def from_mapping(comment_dict: Mapping[str, Any]) -> UserComment:
        return UserComment(
            id=comment_dict["id"],
            user_id=comment_dict["user_id"],
            content=comment_dict["content"],
            likes=comment_dict["likes"],
            post_ts=comment_dict["post_ts"],
            deleted=bool(comment_dict["deleted"]),
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "user_id": self.user_id,
            "content": self.content,
            "likes": self.likes,
            "post_ts": self.post_ts,
            "deleted": self.deleted,
        }

        if include_id:
            res["id"] = self.id

        return res

    # Dunder methods
    def __hash__(self) -> int:
        return self.id
