from __future__ import annotations

from typing import override

from ognisko.services_v2._common import ServiceError


class UserServiceError(ServiceError):
    @override
    def service(self) -> str:
        return "users"

    NOT_FOUND = "not_found"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    VIEWING_PROHIBITED = "viewing_prohibited"


async def lalala() -> UserServiceError.OnSuccess[None]:
    return
