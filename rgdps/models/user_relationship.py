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
    def from_mapping(relationship_dict: Mapping[str, Any]) -> UserRelationship:
        return UserRelationship(
            id=relationship_dict["id"],
            relationship_type=UserRelationshipType(
                relationship_dict["relationship_type"],
            ),
            user1_id=relationship_dict["user1_id"],
            user2_id=relationship_dict["user2_id"],
            post_ts=relationship_dict["post_ts"],
            seen_ts=relationship_dict["seen_ts"],
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
