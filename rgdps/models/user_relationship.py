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
    user1_id: int
    user2_id: int
    post_ts: datetime
    seen_ts: datetime | None

    @staticmethod
    def from_mapping(mapping: Mapping[str, Any]) -> UserRelationship:
        return UserRelationship(
            id=mapping["id"],
            relationship_type=UserRelationshipType(
                mapping["relationship_type"],
            ),
            user1_id=mapping["user1_id"],
            user2_id=mapping["user2_id"],
            post_ts=mapping["post_ts"],
            seen_ts=mapping["seen_ts"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "relationship_type": self.relationship_type.value,
            "user1_id": self.user1_id,
            "user2_id": self.user2_id,
            "post_ts": self.post_ts,
            "seen_ts": self.seen_ts,
        }

        if include_id:
            res["id"] = self.id

        return res
