from __future__ import annotations

from dataclasses import dataclass

from realistikgdps.constants.likes import LikeType


@dataclass
class Like:
    id: int
    target_type: LikeType
    target_id: int
    user_id: int
    value: int
