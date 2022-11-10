from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Mapping
from typing import Optional

from rgdps.constants.songs import SongSource


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

    def __str__(self) -> str:
        return f"{self.author} - {self.name} ({self.id})"

    @staticmethod
    def from_mapping(song_dict: Mapping[str, Any]) -> Song:
        return Song(
            id=song_dict["id"],
            name=song_dict["name"],
            author_id=song_dict["author_id"],
            author=song_dict["author"],
            author_youtube=song_dict["author_youtube"],
            size=song_dict["size"],
            download_url=song_dict["download_url"],
            source=SongSource(song_dict["source"]),
            blocked=song_dict["blocked"],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "author_id": self.author_id,
            "author": self.author,
            "author_youtube": self.author_youtube,
            "size": self.size,
            "download_url": self.download_url,
            "source": self.source.value,
            "blocked": self.blocked,
        }
