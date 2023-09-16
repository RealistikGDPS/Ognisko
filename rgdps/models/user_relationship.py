from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping

from rgdps.constants.users import UserRelationshipType


@dataclass
class UserRelationship:
    id: int
    relationship_type: UserRelationshipType
    user_id: int
    target_user_id: int
    post_ts: datetime
    seen_ts: datetime | None

    @staticmethod
    def from_mapping(mapping: Mapping[str, Any]) -> UserRelationship:
        return UserRelationship(
            id=mapping["id"],
            relationship_type=UserRelationshipType(
                mapping["relationship_type"],
            ),
            user_id=mapping["user_id"],
            target_user_id=mapping["target_user_id"],
            post_ts=mapping["post_ts"],
            seen_ts=mapping["seen_ts"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "relationship_type": self.relationship_type.value,
            "user_id": self.user_id,
            "target_user_id": self.target_user_id,
            "post_ts": self.post_ts,
            "seen_ts": self.seen_ts,
        }

        if include_id:
            res["id"] = self.id

        return res
