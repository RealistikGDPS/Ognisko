from __future__ import annotations

import time
from datetime import datetime

INTERVALS = (
    ("second", 60),
    ("minute", 60),
    ("hour", 24),
    ("day", 30),
    ("month", 12),
    ("year", 100),
    ("decade", 1000),
)


def into_str_ts(ts: datetime) -> str:
    unix_ts = int(time.mktime(ts.timetuple()))
    value = round(time.time()) - unix_ts

    for name, count in INTERVALS:
        if value < count:
            if value == 0:
                value = 1
            if value > 1:
                name += "s"
            return f"{value} {name}"

        value //= count

    return "a long time"


def into_unix_ts(ts: datetime) -> int:
    return int(time.mktime(ts.timetuple()))


def from_unix_ts(ts: int) -> datetime:
    return datetime.fromtimestamp(ts)
