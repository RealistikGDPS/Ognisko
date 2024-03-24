from __future__ import annotations

from datetime import datetime
from typing import TypedDict
from typing import Unpack

from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
from rgdps.models.user_comment import UserComment
from rgdps.common import modelling


ALL_FIELDS = modelling.get_model_fields(UserComment)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(CUSTOMISABLE_FIELDS)


async def from_id(
    ctx: Context,
    comment_id: int,
    include_deleted: bool = False,
) -> UserComment | None:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"
    comment_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_comments WHERE id = :id" + condition,
        {
            "id": comment_id,
        },
    )

    if comment_db is None:
        return None

    return UserComment.from_mapping(comment_db)


async def from_user_id(
    ctx: Context,
    user_id: int,
    include_deleted: bool = False,
) -> list[UserComment]:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"
    comments_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_comments WHERE user_id = :user_id" + condition,
        {"user_id": user_id},
    )

    return [UserComment.from_mapping(comment_db) for comment_db in comments_db]


async def from_user_id_paginated(
    ctx: Context,
    user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[UserComment]:
    condition = ""
    if not include_deleted:
        condition = "AND NOT deleted"

    comments_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_comments WHERE user_id = :user_id {condition} "
        "ORDER BY id DESC LIMIT :limit OFFSET :offset",
        {
            "user_id": user_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [UserComment.from_mapping(comment_db) for comment_db in comments_db]


async def get_user_comment_count(
    ctx: Context,
    user_id: int,
    include_deleted: bool = False,
) -> int:
    return await ctx.mysql.fetch_val(
        (
            "SELECT COUNT(*) FROM user_comments WHERE user_id = :user_id "
            "AND deleted = 0"
            if not include_deleted
            else ""
        ),
        {"user_id": user_id},
    )


async def create(
    ctx: Context,
    user_id: int,
    content: str,
    likes: int = 0,
    post_ts: datetime | None = None,
    deleted: bool = False,
    comment_id: int = 0,
) -> UserComment:
    comment = UserComment(
        id=comment_id,
        user_id=user_id,
        content=content,
        likes=likes,
        post_ts=post_ts or datetime.now(),
        deleted=deleted,
    )

    comment.id = await ctx.mysql.execute(
        f"INSERT INTO user_comments ({_ALL_FIELDS_COMMA}) "
        f"VALUES ({_ALL_FIELDS_COLON})",
        comment.as_dict(include_id=True),
    )

    return comment


class _UserCommentUpdatePartial(TypedDict):
    user_id: int
    content: str
    likes: int
    post_ts: datetime
    deleted: bool


async def update_partial(
    ctx: Context,
    comment_id: int,
    **kwargs: Unpack[_UserCommentUpdatePartial],
    
) -> UserComment | None:
    changed_fields = modelling.unpack_enum_types(kwargs)
    
    await ctx.mysql.execute(
        modelling.update_from_partial_dict("user_comments", comment_id, changed_fields),
        changed_fields,
    )

    return await from_id(ctx, comment_id, include_deleted=True)


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM user_comments")
