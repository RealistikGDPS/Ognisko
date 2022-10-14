from __future__ import annotations

from typing import Union

from realistikgdps import repositories
from realistikgdps.constants.errors import ServiceError
from realistikgdps.models.user import User


def get_as_path(user: User) -> Union[str, ServiceError]:
    """NOTE: This only returns the path to the file as save data can reasonably
    exceed 200MB.
    """

    path = repositories.save_data.from_user_id_as_path(user.id)

    if path is None:
        return ServiceError.SAVE_DATA_NOT_FOUND

    return path


def get(user: User) -> Union[str, ServiceError]:
    """NOTE: This is memory expensive, with saves reasonably exceeding 200MB.
    Please use `get_as_path` when possible."""
    data = repositories.save_data.from_user_id(user.id)

    if data is None:
        return ServiceError.SAVE_DATA_NOT_FOUND

    return data


def save(
    user: User,
    data: str,
) -> Union[None, ServiceError]:
    # TODO: Privilege Check
    # TODO: Validation

    repositories.save_data.create(user.id, data)

    return None
