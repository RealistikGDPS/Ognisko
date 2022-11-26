from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping
from typing import Optional

from rgdps.constants.levels import LevelDemonDifficulty
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlags


@dataclass
class Level:
    id: int
    name: str
    user_id: int
    description: str
    custom_song_id: Optional[int]
    official_song_id: Optional[int]
    version: int
    length: LevelLength
    two_player: bool
    publicity: LevelPublicity
    render_str: str  # Officially called extra string
    game_version: int
    binary_version: int
    upload_ts: datetime
    original_id: Optional[int]

    # Statistics
    downloads: int
    likes: int
    stars: int
    difficulty: LevelDifficulty
    demon_difficulty: Optional[LevelDemonDifficulty]
    coins: int
    coins_verified: bool
    requested_stars: int
    feature_order: int
    search_flags: LevelSearchFlags
    low_detail_mode: bool
    object_count: int
    copy_password: int
    building_time: int
    update_locked: bool
    deleted: bool

    # verification_replay: str

    @property
    def is_demon(self) -> bool:
        return self.stars == 10

    @property
    def is_auto(self) -> bool:
        return self.stars == 1

    @staticmethod
    def from_mapping(level_dict: Mapping[str, Any]) -> Level:
        demon_difficulty = None
        if level_dict["demon_difficulty"] is not None:
            demon_difficulty = LevelDemonDifficulty(level_dict["demon_difficulty"])

        return Level(
            id=level_dict["id"],
            name=level_dict["name"],
            user_id=level_dict["user_id"],
            description=level_dict["description"],
            custom_song_id=level_dict["custom_song_id"],
            official_song_id=level_dict["official_song_id"],
            version=level_dict["version"],
            length=LevelLength(level_dict["length"]),
            two_player=level_dict["two_player"],
            publicity=LevelPublicity(level_dict["publicity"]),
            render_str=level_dict["render_str"],
            game_version=level_dict["game_version"],
            binary_version=level_dict["binary_version"],
            upload_ts=level_dict["upload_ts"],
            original_id=level_dict["original_id"],
            downloads=level_dict["downloads"],
            likes=level_dict["likes"],
            stars=level_dict["stars"],
            difficulty=LevelDifficulty(level_dict["difficulty"]),
            demon_difficulty=demon_difficulty,
            coins=level_dict["coins"],
            coins_verified=bool(level_dict["coins_verified"]),
            requested_stars=level_dict["requested_stars"],
            feature_order=level_dict["feature_order"],
            search_flags=LevelSearchFlags(level_dict["search_flags"]),
            low_detail_mode=bool(level_dict["low_detail_mode"]),
            object_count=level_dict["object_count"],
            copy_password=level_dict["copy_password"],
            building_time=level_dict["building_time"],
            update_locked=bool(level_dict["update_locked"]),
            deleted=bool(level_dict["deleted"]),
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "custom_song_id": self.custom_song_id,
            "official_song_id": self.official_song_id,
            "version": self.version,
            "length": self.length.value,
            "two_player": self.two_player,
            "publicity": self.publicity.value,
            "render_str": self.render_str,
            "game_version": self.game_version,
            "binary_version": self.binary_version,
            "upload_ts": self.upload_ts,
            "original_id": self.original_id,
            "downloads": self.downloads,
            "likes": self.likes,
            "stars": self.stars,
            "difficulty": self.difficulty.value,
            "demon_difficulty": self.demon_difficulty.value
            if self.demon_difficulty is not None
            else None,
            "coins": self.coins,
            "coins_verified": self.coins_verified,
            "requested_stars": self.requested_stars,
            "feature_order": self.feature_order,
            "search_flags": self.search_flags.value,
            "low_detail_mode": self.low_detail_mode,
            "object_count": self.object_count,
            "copy_password": self.copy_password,
            "building_time": self.building_time,
            "update_locked": self.update_locked,
            "deleted": self.deleted,
        }

        if include_id:
            res["id"] = self.id

        return res
