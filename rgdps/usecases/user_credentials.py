from __future__ import annotations

from rgdps import logger
from rgdps import repositories
from rgdps.common import hashes
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.user_credentials import CredentialVersion
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User


async def authenticate_plain(
    ctx: Context,
    user_id: int,
    password: str,
) -> User | ServiceError:
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    if not user.privileges & UserPrivileges.USER_AUTHENTICATE:
        return ServiceError.AUTH_NO_PRIVILEGE

    creds = await repositories.user_credential.from_user_id(ctx, user_id)

    if creds is None:
        logger.warning(
            "User has no credentials attached to them.",
            extra={
                "user_id": user_id,
            },
        )
        return ServiceError.AUTH_NOT_FOUND

    # Credential update.
    if creds.version == CredentialVersion.PLAIN_BCRYPT:
        # Compare the password with the stored hash.
        if not await hashes.compare_bcrypt(
            creds.value,
            password,
        ):
            return ServiceError.AUTH_PASSWORD_MISMATCH

        # Update the credential to the latest version.
        await repositories.user_credential.delete_from_id(ctx, creds.id)

        await repositories.user_credential.create(
            ctx,
            user_id,
            CredentialVersion.GJP2_BCRYPT,
            password,
        )

        logger.info(
            "Migrated user credential to latest version.",
            extra={
                "user_id": user_id,
                "old_version": creds.version,
                "new_version": CredentialVersion.GJP2_BCRYPT,
            },
        )

        return user

    gjp2_pw = hashes.hash_gjp2(password)

    if not await hashes.compare_bcrypt(
        creds.value,
        gjp2_pw,
    ):
        return ServiceError.AUTH_PASSWORD_MISMATCH

    return user


async def authenticate_from_name_plain(
    ctx: Context,
    username: str,
    password: str,
) -> User | ServiceError:
    user = await repositories.user.from_name(ctx, username)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    return await authenticate_plain(
        ctx,
        user.id,
        password,
    )


async def change_password(
    ctx: Context,
    user_id: int,
    password: str,
) -> None:
    await repositories.user_credential.delete_from_user_id(ctx, user_id)

    gjp2_pw = hashes.hash_gjp2(password)

    await repositories.user_credential.create(
        ctx,
        user_id,
        CredentialVersion.GJP2_BCRYPT,
        gjp2_pw,
    )
