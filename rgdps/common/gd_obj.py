from __future__ import annotations

import base64
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union

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
) -> GDSerialisable:
    return {
        1: user.username,
        2: user.id,
        3: user.stars,
        4: user.demons,
        6: 0,  # TODO: Implement rank
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
        30: 0,  # TODO: Implement rank
        31: friend_status.value,
        43: user.spider,
        44: user.twitter_name or "",
        45: user.twitch_name or "",
        46: 0,  # TODO: Diamonds, which require save data parsing....
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
        12: level.official_song_id or 0,
        13: level.game_version,
        14: level.likes,
        15: level.length.value,
        17: level.stars == 10,  # is demon
        18: level.stars,
        19: level.feature_order,
        25: level.stars == 1,  # is auto
        30: level.original_id or 0,
        31: 1 if level.original_id else 0,
        35: level.custom_song_id or 0,
        37: level.coins,
        38: 1 if level.coins_verified else 0,
        39: level.requested_stars,
        42: 1 if level.search_flags & LevelSearchFlags.EPIC else 0,  # is epic
        43: level.demon_difficulty.value if level.demon_difficulty else 0,
    }
