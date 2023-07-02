from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.common.validators import Base64String
from rgdps.constants.errors import ServiceError
from rgdps.constants.likes import LikeType
from rgdps.constants.responses import GenericResponse
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User
from rgdps.usecases import likes
from rgdps.usecases import user_comments

PAGE_SIZE = 10


async def view_user_comments(
    target_id: int = Form(..., alias="accountID"),
    page: int = Form(..., alias="page"),
    ctx: HTTPContext = Depends(),
) -> str:
    result = await user_comments.get_user(ctx, target_id, page)

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to view comments of {target_id} with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    response = "|".join(
        gd_obj.dumps(gd_obj.create_user_comment(comment), sep="~")
        for comment in result.comment
    )
    response += "#" + gd_obj.create_pagination_info(result.total, page, PAGE_SIZE)

    logger.info(f"Successfully viewed comments of {target_id}.")
    return response


async def post_user_comment(
    ctx: HTTPContext = Depends(),
    user: User = Depends(
        authenticate_dependency(
            required_privileges=UserPrivileges.USER_CREATE_USER_COMMENTS,
        ),
    ),
    content: Base64String = Form(..., alias="comment"),
) -> str:
    result = await user_comments.create(ctx, user, content)

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to post comment on {user}'s profile with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"{user} successfully posted a profile comment.")
    return str(GenericResponse.SUCCESS)


# TODO: MOVE
async def like_target(
    ctx: HTTPContext = Depends(),
    user: User = Depends(
        authenticate_dependency(required_privileges=UserPrivileges.COMMENTS_LIKE),
    ),
    target_type: LikeType = Form(..., alias="type"),
    target_id: int = Form(..., alias="itemID"),
    is_positive: bool = Form(..., alias="like"),
) -> str:

    result = None
    if target_type is LikeType.USER_COMMENT:
        result = await likes.like_comment(ctx, user.id, target_id, int(is_positive))
    elif target_type is LikeType.LEVEL:
        result = await likes.like_level(ctx, user.id, target_id, int(is_positive))

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to like {target_type!r} {target_id} with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"{user} successfully liked {target_type!r} {target_id}.")
    return str(GenericResponse.SUCCESS)


async def delete_user_comment(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    comment_id: int = Form(..., alias="commentID"),
) -> str:
    result = await user_comments.delete(ctx, user, comment_id)

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to delete comment {comment_id} with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"{user} successfully deleted comment {comment_id}.")
    return str(GenericResponse.SUCCESS)
