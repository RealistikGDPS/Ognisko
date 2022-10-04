from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from realistikgdps.constants.songs import SongSource


@dataclass
class Song:
    id: int
    name: str
    author_id: int
    author: str
    author_youtube: Optional[str]
    size: float
    download_url: str
    source: SongSource
    blocked: bool
