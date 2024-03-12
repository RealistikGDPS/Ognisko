from __future__ import annotations

import urllib.parse
from typing import Callable
from typing import NamedTuple

from rgdps.common import hashes
from rgdps.common.time import into_str_ts
from rgdps.common.time import into_unix_ts
from rgdps.common.typing import SupportsStr
from rgdps.constants.daily_chests import DailyChestType
from rgdps.constants.friends import FriendStatus
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.users import UserPrivileges
from rgdps.models.daily_chest import DailyChest
from rgdps.models.friend_request import FriendRequest
from rgdps.models.level import Level
from rgdps.models.level_comment import LevelComment
from rgdps.models.message import Message
from rgdps.models.message import MessageDirection
from rgdps.models.song import Song
from rgdps.models.user import User
from rgdps.models.user_comment import UserComment
from rgdps.models.user_relationship import UserRelationship

GDSerialisable = dict[int | str, int | str | float]


def _serialise_gd_object(obj: GDSerialisable, sep: str = ":") -> str:
    return sep.join(str(key) + sep + str(value) for key, value in obj.items())


def dumps(
    obj: GDSerialisable | list[GDSerialisable],
    sep: str = ":",
    list_sep: str = ":",
) -> str:
    if isinstance(obj, list):
        return list_sep.join(_serialise_gd_object(gd_obj, sep) for gd_obj in obj)
    else:
        return _serialise_gd_object(obj, sep)


def loads[
    KT, VT
](
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
    messages_count: int = 0,
    friend_request_count: int = 0,
    friend_count: int = 0,
) -> GDSerialisable:
    badge_level = 0
    if user.privileges & UserPrivileges.USER_DISPLAY_ELDER_BADGE:
        badge_level = 2
    elif user.privileges & UserPrivileges.USER_DISPLAY_MOD_BADGE:
        badge_level = 1

    return {
        1: user.username,
        2: user.id,
        3: user.stars,
        4: user.demons,
        6: rank,
        7: user.id,
        8: user.creator_points,
        9: user.icon,
        10: user.primary_colour,
        11: user.secondary_colour,
        13: user.coins,
        14: user.display_type,
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
        38: messages_count,
        39: friend_request_count,
        40: friend_count,
        43: user.spider,
        44: user.twitter_name or "",
        45: user.twitch_name or "",
        46: user.diamonds,
        48: user.explosion,
        49: badge_level,
        50: user.comment_privacy.value,
        51: user.glow_colour,
        52: user.moons,
        53: user.swing_copter,
        54: user.jetpack,
    }


def create_user_relationship(relationship: UserRelationship) -> GDSerialisable:
    return {
        41: 0 if relationship.seen_ts else 1,
    }


def create_user_str(user: User) -> str:
    return f"{user.id}:{user.username}:{user.id}"


def create_user_comment(comment: UserComment, user: User) -> GDSerialisable:
    return {
        2: hashes.encode_base64(comment.content),
        4: comment.likes,
        6: comment.id,
        9: into_str_ts(comment.post_ts),
        12: user.comment_colour,
    }


def create_friend_request(friend_request: FriendRequest) -> GDSerialisable:
    return {
        32: friend_request.id,
        35: hashes.encode_base64(friend_request.message),
        37: into_str_ts(friend_request.post_ts),
        41: 0 if friend_request.seen_ts else 1,
    }


def create_friend_request_author(user: User) -> GDSerialisable:
    return {
        1: user.username,
        2: user.id,
        9: user.icon,
        10: user.primary_colour,
        11: user.secondary_colour,
        14: user.display_type,
        15: 2 if user.glow else 0,
        16: user.id,
    }


def create_level_comment(
    comment: LevelComment,
    user: User,
    include_level_id: bool = False,
) -> GDSerialisable:
    badge_level = 0
    if user.privileges & UserPrivileges.USER_DISPLAY_ELDER_BADGE:
        badge_level = 2
    elif user.privileges & UserPrivileges.USER_DISPLAY_MOD_BADGE:
        badge_level = 1

    ret: GDSerialisable = {
        2: hashes.encode_base64(comment.content),
        3: user.id,
        4: comment.likes,
        6: comment.id,
        8: user.id,
        9: into_str_ts(comment.post_ts),
        10: comment.percent or 0,
        11: badge_level,
        12: user.comment_colour,
    }

    if include_level_id:
        ret[1] = comment.level_id

    return ret


def create_level_comment_author(user: User) -> GDSerialisable:
    return {
        1: user.username,
        9: user.icon,
        10: user.primary_colour,
        11: user.secondary_colour,
        14: user.display_type,
        15: 2 if user.glow else 0,
        16: user.id,
    }


def create_song(song: Song) -> GDSerialisable:
    return {
        1: song.id,
        2: song.name,
        3: song.author_id,
        4: song.author,
        5: song.size,
        7: song.author_youtube or "",
        8: int(not song.blocked),  # Is scouted (allowed)
        10: urllib.parse.quote(song.download_url, safe=""),
    }


def create_level_minimal(level: Level) -> GDSerialisable:
    """Minimal level data for level search."""

    if level.description:
        description_b64 = hashes.encode_base64(level.description)
    else:
        description_b64 = ""

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
        40: int(level.low_detail_mode),
        42: 1 if level.search_flags & LevelSearchFlag.EPIC else 0,
        43: level.demon_difficulty.value if level.demon_difficulty else 0,
        45: level.object_count,
        46: level.building_time,
        47: level.building_time,
        52: joined_string(level.song_ids),
        53: joined_string(level.sfx_ids),
        # TODO: Is this correct lolll
        57: into_unix_ts(level.upload_ts),
    }


FREE_COPY_HASH = hashes.hash_level_password(1)

def create_level(level: Level, level_data: str, schedule_id: int = 0) -> GDSerialisable:
    return create_level_minimal(level) | {
        4: level_data,
        27: FREE_COPY_HASH,
        28: into_str_ts(level.upload_ts),
        29: into_str_ts(level.update_ts),
        36: level.render_str,
        41: schedule_id,
    }


def create_message(
    message: Message,
    user: User,
    message_direction: MessageDirection,
) -> GDSerialisable:

    return {
        1: message.id,
        2: user.id,
        3: user.id,
        4: hashes.encode_base64(message.subject),
        5: encrypt_message_content_string(message.content),
        6: user.username,
        7: into_str_ts(message.post_ts),
        8: message.seen_ts is not None,
        9: 0 if message_direction is MessageDirection.RECEIVED else 1,
    }


def create_level_security_str(level: Level) -> str:
    level_id_str = str(level.id)

    return (
        f"{level_id_str[0]}{level_id_str[-1]}{level.stars}{int(level.coins_verified)}"
    )


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


def create_level_metadata_security_str(level: Level, schedule_id) -> str:
    return ",".join(
        (
            str(level.user_id),
            str(level.stars),
            "1" if level.is_demon else "0",
            str(level.id),
            "1" if level.coins_verified else "0",
            str(level.feature_order),
            "1",
            str(schedule_id),
        ),
    )


def create_level_metadata_security_str_hashed(level: Level, schedule_id) -> str:
    return hashes.hash_sha1(
        create_level_metadata_security_str(level, schedule_id) + "xI25fpAapCQg",
    )


def create_pagination_info(total: int, page: int, page_size: int) -> str:
    offset = page * page_size  # NOTE: page starts at 0
    return f"{total}:{offset}:{page_size}"


def comma_separated_ints(data: str) -> list[int]:
    """Parses a list of ints in the from `(1,2,3,4)`."""

    return [int(x) for x in data[1:-1].split(",")]


def joined_string(*data: SupportsStr, separator: str = ",") -> str:
    return separator.join(str(x) for x in data)


def create_chest_rewards(chest: DailyChest) -> str:
    return joined_string(
        chest.mana,
        chest.diamonds,
        0,  # TODO: Shards,
        chest.demon_keys,
    )


EMPTY_CHEST = "0,0,0,0"


def create_chest_rewards_str(
    chest: DailyChest | None,
    user_id: int,
    check_string: str,
    device_id: str,
    small_chest_time: int,
    small_chest_count: int,
    large_chest_time: int,
    large_chest_count: int,
) -> str:
    if chest is None:
        small_chest_items = EMPTY_CHEST
        large_chest_items = EMPTY_CHEST
        reward_type = 0
    elif chest.type is DailyChestType.SMALL:
        small_chest_items = create_chest_rewards(chest)
        large_chest_items = EMPTY_CHEST
        reward_type = 1
    else:
        small_chest_items = EMPTY_CHEST
        large_chest_items = create_chest_rewards(chest)
        reward_type = 2

    return joined_string(
        hashes.random_string(5),
        user_id,
        check_string,
        device_id,
        user_id,
        small_chest_time,
        small_chest_items,
        small_chest_count,
        large_chest_time,
        large_chest_items,
        large_chest_count,
        reward_type,
        separator=":",
    )


def create_chest_security_str(response: str) -> str:
    return hashes.hash_sha1(response + "pC26fpYaQCtg")


class EncryptedChestResponse(NamedTuple):
    response: str
    prefix: str


def encrypt_chest_response(response: str) -> EncryptedChestResponse:
    prefix = hashes.random_string(5)
    encoded = hashes.encrypt_chests(response)

    return EncryptedChestResponse(
        response=encoded,
        prefix=prefix,
    )


def decrypt_chest_check_string(check_string: str) -> str:
    return hashes.decrypt_chest_check(check_string)


def encrypt_message_content_string(content: str) -> str:
    return hashes.encrypt_message_content(content)


def decrypt_message_content_string(content: str) -> str:
    return hashes.decrypt_message_content(content)


def comment_ban_string(
    remaining_duration: int,
    ban_reason: str,
) -> str:
    return f"temp_{remaining_duration}_{ban_reason}"
