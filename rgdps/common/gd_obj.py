from __future__ import annotations

import base64
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union

from rgdps.common import hashes
from rgdps.common.time import into_str_ts
from rgdps.constants.friends import FriendStatus
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelSearchFlags
from rgdps.models.level import Level
from rgdps.models.song import Song
from rgdps.models.user import User
from rgdps.models.user_comment import UserComment

GDSerialisable = dict[Union[int, str], Union[int, str, float]]


def dumps(obj: GDSerialisable, sep: str = ":") -> str:
    return sep.join(str(key) + sep + str(value) for key, value in obj.items())


VT = TypeVar("VT")
KT = TypeVar("KT")


def loads(
    data: str,
    sep: str = ":",
    key_cast: Callable[[str], KT] = int,
    value_cast: Callable[[str], VT] = str,
) -> dict[KT, VT]:

    data_split = data.split(sep)

    if len(data_split) % 2 != 0:
        raise ValueError("Data does not have matching key/value pairs.")

    data_iter = iter(data_split)

    return {
        key_cast(key): value_cast(value) for key, value in zip(data_iter, data_iter)
    }


def create_profile(
    user: User,
    friend_status: FriendStatus = FriendStatus.NONE,
    rank: int = 0,
) -> GDSerialisable:
    return {
        1: user.username,
        2: user.id,
        3: user.stars,
        4: user.demons,
        6: rank,
        7: user.id,
        8: user.creator_points,
        9: user.display_type,
        10: user.primary_colour,
        11: user.secondary_colour,
        13: user.coins,
        14: user.icon,
        15: 0,
        16: user.id,
        17: user.user_coins,
        18: user.message_privacy.value,
        19: user.friend_privacy.value,
        20: user.youtube_name or "",
        21: user.icon,
        22: user.ship,
        23: user.ball,
        24: user.ufo,
        25: user.wave,
        26: user.robot,
        28: int(user.glow),
        29: 1,  # Is Registered
        30: rank,
        31: friend_status.value,
        43: user.spider,
        44: user.twitter_name or "",
        45: user.twitch_name or "",
        46: user.diamonds,
        48: user.explosion,
        49: 0,  # TODO: Badge level with privileges.
        50: user.comment_privacy.value,
    }


def create_user_comment(comment: UserComment) -> GDSerialisable:
    return {
        2: base64.b64encode(comment.content.encode()).decode(),
        4: comment.likes,
        6: comment.id,
        9: into_str_ts(comment.post_ts),
        12: "0,0,0",  # TODO: Colour system (privilege bound)
    }


def create_song(song: Song) -> GDSerialisable:
    return {
        1: song.id,
        2: song.name,
        3: song.author_id,
        4: song.author,
        5: song.size,
        7: song.author_youtube or "",
        10: song.download_url,
    }


def create_level_minimal(level: Level) -> GDSerialisable:
    """Minimal level data for level search."""

    description_b64 = base64.b64encode(level.description.encode()).decode()
    return {
        1: level.id,
        2: level.name,
        3: description_b64,
        5: level.version,
        6: level.user_id,
        8: 10 if level.difficulty != LevelDifficulty.NA else 0,
        9: level.difficulty.value,
        10: level.downloads,
        12: level.official_song_id or 0,
        13: level.game_version,
        14: level.likes,
        15: level.length.value,
        17: int(level.is_demon),
        18: level.stars,
        19: level.feature_order,
        25: int(level.is_auto),
        30: level.original_id or 0,
        31: 1 if level.original_id else 0,
        35: level.custom_song_id or 0,
        37: level.coins,
        38: 1 if level.coins_verified else 0,
        39: level.requested_stars,
        42: 1 if level.search_flags & LevelSearchFlags.EPIC else 0,  # is epic
        43: level.demon_difficulty.value if level.demon_difficulty else 0,
        45: level.object_count,
    }


def create_level(level: Level, level_data: str) -> GDSerialisable:
    return create_level_minimal(level) | {
        4: level_data,
        27: hashes.hash_level_password(level.copy_password),
        28: into_str_ts(level.upload_ts),
        29: into_str_ts(level.upload_ts), # TODO: This is wrong. Meant to be last updated.
        36: level.render_str,
    }


# TODO: These should probably be renamed to be more concise.
def create_level_security_str(level: Level) -> str:
    level_id_str = str(level.id)

    return f"{level_id_str[0]}{level_id_str[-1]}{level.stars}{level.coins}"


def create_search_security_str(levels: list[Level]) -> str:
    return hashes.hash_sha1(
        "".join(create_level_security_str(level) for level in levels) + "xI25fpAapCQg",
    )


def create_level_data_security_str(level_data: str) -> str:
    res = ""
    size = len(level_data) // 40
    for i in range(40):
        res += level_data[i * size]

    return hashes.hash_sha1(res + "xI25fpAapCQg")


def create_level_metadata_security_str(level: Level) -> str:
    return ",".join(
        (
            str(level.user_id),
            str(level.stars),
            "1" if level.is_demon else "0",
            str(level.id),
            "1" if level.coins_verified else "0",
            str(level.feature_order),
            str(level.copy_password),
            "0",
        ),
    )


def create_level_metadata_security_str_hashed(level: Level) -> str:
    return hashes.hash_sha1(create_level_metadata_security_str(level) + "xI25fpAapCQg")


def create_pagination_info(total: int, page: int, page_size: int) -> str:
    offset = page * page_size
    return f"{total}:{offset}:{page_size}"
