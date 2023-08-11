from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping


@dataclass
class LevelComment:
    id: int
    user_id: int
    level_id: int
    content: str
    percent: int
    likes: int
    post_ts: datetime
    deleted: bool

    @staticmethod
    def from_mapping(mapping: Mapping[str, Any]) -> LevelComment:
        return LevelComment(
            id=mapping["id"],
            user_id=mapping["user_id"],
            level_id=mapping["level_id"],
            content=mapping["content"],
            percent=mapping["percent"],
            likes=mapping["likes"],
            post_ts=mapping["post_ts"],
            deleted=mapping["deleted"],
        )

    def as_dict(self, *, include_id: bool = True) -> dict[str, Any]:
        mapping = {
            "user_id": self.user_id,
            "level_id": self.level_id,
            "content": self.content,
            "percent": self.percent,
            "likes": self.likes,
            "post_ts": self.post_ts,
            "deleted": self.deleted,
        }

        if include_id:
            mapping["id"] = self.id or None

        return mapping
