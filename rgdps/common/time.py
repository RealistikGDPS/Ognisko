from __future__ import annotations

import time
from datetime import datetime

INTERVALS = (
    ("second", 60),
    ("minute", 60),
    ("hour", 60),
    ("day", 24),
    ("month", 30),
    ("year", 12),
    ("decade", 100),
)


def into_str_ts(ts: datetime) -> str:
    unix_ts = int(time.mktime(ts.timetuple()))
    value = int(time.time()) - unix_ts

    for idx, (name, count) in enumerate(INTERVALS):
        if value < INTERVALS[idx + 1][1]:
            if value == 0:
                value = 1
            if value > 1:
                name += "s"
            return f"{value} {name}"

        value //= count

    return "a long time"
