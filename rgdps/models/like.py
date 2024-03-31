from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from rgdps.constants.likes import LikeType


@dataclass
class Like:
    id: int
    target_type: LikeType
    target_id: int
    user_id: int
    value: int

    @staticmethod
    def from_mapping(like_dict: Mapping[str, Any]) -> Like:
        return Like(
            id=like_dict["id"],
            target_type=LikeType(like_dict["target_type"]),
            target_id=like_dict["target_id"],
            user_id=like_dict["user_id"],
            value=like_dict["value"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res: dict[str, Any] = {
            "target_type": self.target_type.value,
            "target_id": self.target_id,
            "user_id": self.user_id,
            "value": self.value,
        }

        if include_id:
            res["id"] = self.id or None

        return res

    # Dunder methods
    def __hash__(self) -> int:
        return self.id
