from __future__ import annotations

from enum import Enum


class ServiceError(str, Enum):
    AUTH_NOT_FOUND = "auth.not_found"
    AUTH_PASSWORD_MISMATCH = "auth.password_mismatch"
    PROFILE_USER_BLOCKED = "profile.user_blocked"
    PROFILE_USER_NOT_FOUND = "profile.user_not_found"
    PROFILE_BLOCKED_BY_USER = "profile.blocked_by_user"
    COMMENTS_INVALID_CONTENT = "comments.invalid_content"
    COMMENTS_NOT_FOUND = "comments.not_found"
    LIKES_ALREADY_LIKED = "likes.already_liked"
    LIKES_OWN_TARGET = "likes.own_target"
    LIKES_INVALID_TARGET = "likes.invalid_target"
    SONGS_NOT_FOUND = "songs.not_found"
    SAVE_DATA_NOT_FOUND = "save_data.not_found"
    LEVELS_NO_UPDATE_PERMISSION = "levels.no_update_permission"
    LEVELS_INVALID_CUSTOM_SONG = "levels.invalid_custom_song"
    LEVELS_NOT_FOUND = "levels.not_found"
    LEVELS_UPDATE_LOCKED = "levels.update_locked"
