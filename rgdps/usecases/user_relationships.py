from __future__ import annotations

from datetime import datetime
from typing import NamedTuple

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.users import UserRelationshipType
from rgdps.models.user import User
from rgdps.models.user_relationship import UserRelationship


class UserRelationshipResponse(NamedTuple):
    relationship: UserRelationship
    user: User  # It's the user2.


class PaginatedUserRelationshipResponse(NamedTuple):
    relationships: list[UserRelationshipResponse]
    total: int


async def get_user(
    ctx: Context,
    user_id: int,
    relationship_type: UserRelationshipType,
) -> PaginatedUserRelationshipResponse | ServiceError:

    relationships = await repositories.user_relationship.from_user_id(
        ctx,
        user_id,
        relationship_type,
        include_deleted=False,
    )

    relationships_responses = []
    for relationship in relationships:
        user = await repositories.user.from_id(ctx, relationship.user2_id)

        if user is None:
            continue

        relationships_responses.append(
            UserRelationshipResponse(relationship, user),
        )

    relationship_count = (
        await repositories.user_relationship.get_user_relationship_count(
            ctx,
            user_id,
            relationship_type,
        )
    )

    return PaginatedUserRelationshipResponse(
        relationships_responses,
        relationship_count,
    )


async def mark_all_as_seen(
    ctx: Context,
    user_id: int,
    relationship_type: UserRelationshipType,
) -> ServiceError | None:

    seen_ts = datetime.utcnow()
    await repositories.user_relationship.mark_all_as_seen(
        ctx,
        user_id,
        relationship_type,
        seen_ts,
    )


async def create(
    ctx: Context,
    user1_id: int,
    user2_id: int,
    relationship_type: UserRelationshipType,
) -> UserRelationship | ServiceError:
    
    if user1_id == user2_id:
        return ServiceError.RELATIONSHIP_INVALID_TARGET_ID

    exists = await repositories.user_relationship.check_relationship_exists(
        ctx,
        user1_id,
        user2_id,
        relationship_type,
    )

    if exists:
        return ServiceError.RELATIONSHIP_EXISTS

    relationship = await repositories.user_relationship.create(
        ctx,
        user1_id,
        user2_id,
        relationship_type,
    )
    return relationship


async def remove_friendship(
    ctx: Context,
    user1_id: int,
    user2_id: int,
) -> UserRelationship | ServiceError:
    
    if user1_id == user2_id:
        return ServiceError.RELATIONSHIP_INVALID_TARGET_ID

    relationship = await delete(
        ctx,
        user1_id,
        user2_id,
        UserRelationshipType.FRIEND,
    )

    await delete(  # This is to remove the other side of the relationship.
        ctx,
        user2_id,
        user1_id,
        UserRelationshipType.FRIEND,
    )

    return relationship


async def delete(
    ctx: Context,
    user1_id: int,
    user2_id: int,
    relationship_type: UserRelationshipType,
) -> UserRelationship | ServiceError:
    relationship = await repositories.user_relationship.from_user_ids(
        ctx,
        user1_id,
        user2_id,
        relationship_type,
    )

    if relationship is None:
        return ServiceError.RELATIONSHIP_NOT_FOUND

    if relationship.user1_id != user1_id:
        return ServiceError.RELATIONSHIP_INVALID_OWNER

    relationship = await repositories.user_relationship.update_partial(
        ctx,
        relationship.id,
        deleted=True,
    )

    if relationship is None:
        return ServiceError.RELATIONSHIP_NOT_FOUND

    return relationship
