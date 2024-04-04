from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from rgdps.common import modelling
from rgdps.common.context import Context
from rgdps.constants.level_comments import LevelCommentSorting
from rgdps.models.level_comment import LevelComment

ALL_FIELDS = modelling.get_model_fields(LevelComment)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


async def from_id(
    ctx: Context,
    comment_id: int,
    include_deleted: bool = False,
) -> LevelComment | None:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"

    level_db = await ctx.mysql.fetch_one(
        f"SELECT {ALL_FIELDS} FROM level_comments WHERE id = :comment_id" + condition,
        {
            "comment_id": comment_id,
        },
    )

    if level_db is None:
        return None

    return LevelComment.from_mapping(level_db)


async def create(
    ctx: Context,
    user_id: int,
    level_id: int,
    content: str,
    percent: int,
    likes: int = 0,
    post_ts: datetime | None = None,
    deleted: bool = False,
    comment_id: int = 0,
) -> LevelComment:
    comment = LevelComment(
        id=comment_id,
        user_id=user_id,
        level_id=level_id,
        content=content,
        percent=percent,
        likes=likes,
        post_ts=post_ts or datetime.now(),
        deleted=deleted,
    )
    # Uses all fields due to supporting comment_id
    comment.id = await ctx.mysql.execute(
        f"INSERT INTO level_comments ({_ALL_FIELDS_COMMA}) VALUES ({_ALL_FIELDS_COLON})",
        comment.as_dict(include_id=True),
    )
    return comment


class _LevelCommentUpdatePartial(TypedDict):
    user_id: NotRequired[int]
    level_id: NotRequired[int]
    content: NotRequired[str]
    percent: NotRequired[int]
    likes: NotRequired[int]
    post_ts: NotRequired[datetime]
    deleted: NotRequired[bool]


async def update_partial(
    ctx: Context,
    comment_id: int,
    **kwargs: Unpack[_LevelCommentUpdatePartial],
) -> LevelComment | None:
    changed_fields = modelling.unpack_enum_types(kwargs)

    await ctx.mysql.execute(
        modelling.update_from_partial_dict(
            "level_comments",
            comment_id,
            changed_fields,
        ),
        changed_fields,
    )

    return await from_id(ctx, comment_id, include_deleted=True)


async def from_level_id_paginated(
    ctx: Context,
    level_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
    sorting: LevelCommentSorting = LevelCommentSorting.NEWEST,
) -> list[LevelComment]:
    condition = ""
    if not include_deleted:
        condition = "AND NOT deleted"

    order_by = "id"
    if sorting is LevelCommentSorting.MOST_LIKED:
        order_by = "likes"

    comments_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM "
        f"level_comments WHERE level_id = :level_id {condition} "
        f"ORDER BY {order_by} DESC LIMIT :limit OFFSET :offset",
        {
            "level_id": level_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [LevelComment.from_mapping(comment_db) for comment_db in comments_db]


async def from_user_id_paginated(
    ctx: Context,
    user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
    sorting: LevelCommentSorting = LevelCommentSorting.NEWEST,
) -> list[LevelComment]:
    condition = ""
    if not include_deleted:
        condition = "AND NOT deleted"

    order_by = "id"
    if sorting is LevelCommentSorting.MOST_LIKED:
        order_by = "likes"

    comments_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM "
        f"level_comments WHERE user_id = :user_id {condition} "
        f"ORDER BY {order_by} DESC LIMIT :limit OFFSET :offset",
        {
            "user_id": user_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [LevelComment.from_mapping(comment_db) for comment_db in comments_db]


async def get_count_from_level(
    ctx: Context,
    level_id: int,
    include_deleted: bool = False,
) -> int:
    return await ctx.mysql.fetch_val(
        (
            "SELECT COUNT(*) FROM level_comments WHERE level_id = :level_id "
            "AND deleted = 0"
            if not include_deleted
            else ""
        ),
        {"level_id": level_id},
    )


async def get_count_from_user(
    ctx: Context,
    user_id: int,
    include_deleted: bool = False,
) -> int:
    return await ctx.mysql.fetch_val(
        (
            "SELECT COUNT(*) FROM level_comments WHERE user_id = :user_id "
            "AND deleted = 0"
            if not include_deleted
            else ""
        ),
        {"user_id": user_id},
    )


async def get_count(
    ctx: Context,
) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM level_comments")
