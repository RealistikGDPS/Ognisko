from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ognisko.constants.level_schedules import LevelScheduleType


@dataclass
class LevelSchedule:
    id: int
    type: LevelScheduleType
    level_id: int
    start_time: datetime
    end_time: datetime
    scheduled_by_id: int | None

    @staticmethod
    def from_mapping(mapping: Mapping[str, Any]) -> LevelSchedule:
        return LevelSchedule(
            id=mapping["id"],
            type=LevelScheduleType(mapping["type"]),
            level_id=mapping["level_id"],
            start_time=mapping["start_time"],
            end_time=mapping["end_time"],
            scheduled_by_id=mapping["scheduled_by_id"],
        )

    def as_dict(self, *, include_id: bool = True) -> dict[str, Any]:
        mapping = {
            "type": self.type.value,
            "level_id": self.level_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "scheduled_by_id": self.scheduled_by_id,
        }

        if include_id:
            mapping["id"] = self.id or None

        return mapping
