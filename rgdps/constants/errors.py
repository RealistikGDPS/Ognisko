from __future__ import annotations

from enum import Enum


class ServiceError(str, Enum):
    AUTH_NOT_FOUND = "auth.not_found"
    AUTH_PASSWORD_MISMATCH = "auth.password_mismatch"
    AUTH_NO_PRIVILEGE = "auth.no_privilege"

    USER_EMAIL_EXISTS = "user.email_exists"
    USER_USERNAME_EXISTS = "user.username_exists"
    USER_IS_BLOCKED = "user.is_blocked"
    USER_NOT_FOUND = "user.not_found"
    USER_BLOCKED_BY_USER = "user.blocked_by_user"
    USER_PROFILE_PRIVATE = "user.profile_private"
    USER_COMMENTS_PRIVATE = "user.comments_private"

    COMMENTS_INVALID_CONTENT = "comments.invalid_content"
    COMMENTS_NOT_FOUND = "comments.not_found"
    COMMENTS_INVALID_OWNER = "comments.invalid_owner"
    COMMENTS_TARGET_NOT_FOUND = "comments.target_not_found"

    FRIEND_REQUEST_MESSAGE_INVALID_CONTENT = "friend_request.message_invalid_content"
    FRIEND_REQUEST_NOT_FOUND = "friend_request.not_found"
    FRIEND_REQUEST_EXISTS = "friend_request.exists"
    FRIEND_REQUEST_INVALID_OWNER = "friend_request.invalid_owner"
    FRIEND_REQUEST_INVALID_TARGET_ID = "friend_request.invalid_target_id"

    RELATIONSHIP_NOT_FOUND = "relationship.not_found"
    RELATIONSHIP_EXISTS = "relationship.exists"
    RELATIONSHIP_INVALID_OWNER = "relationship.invalid_owner"
    RELATIONSHIP_INVALID_TARGET_ID = "relationship.invalid_target_id"

    LIKES_ALREADY_LIKED = "likes.already_liked"
    LIKES_OWN_TARGET = "likes.own_target"
    LIKES_INVALID_TARGET = "likes.invalid_target"

    SONGS_NOT_FOUND = "songs.not_found"

    SAVE_DATA_NOT_FOUND = "save_data.not_found"

    LEVELS_NO_UPDATE_PERMISSION = "levels.no_update_permission"
    LEVELS_INVALID_CUSTOM_SONG = "levels.invalid_custom_song"
    LEVELS_NOT_FOUND = "levels.not_found"
    LEVELS_UPDATE_LOCKED = "levels.update_locked"
    LEVELS_NO_DELETE_PERMISSION = "levels.no_delete_permission"
    LEVELS_NO_UPLOAD_PERMISSION = "levels.no_upload_permission"

    MESSAGES_INVALID_RECIPIENT = "messages.invalid_recipient"
    DAILY_CHESTS_ALREADY_CLAIMED = "daily_chests.already_claimed"
