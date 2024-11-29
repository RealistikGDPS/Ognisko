from __future__ import annotations

from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from enum import EnumMeta
from typing import Self
from typing import TypeGuard

from ognisko.utilities.enum import StrEnum


class _CombinedMeta(EnumMeta, ABCMeta):
    pass


class ServiceError(StrEnum, ABC, metaclass=_CombinedMeta):
    type OnSuccess[T] = T | Self

    @abstractmethod
    def service(self) -> str:
        """The prefix of the service for the error. Will resolve to `<service>.<error>`."""

    def resolve_name(self) -> str:
        """A name of the error involving the service name."""
        return f"{self.service()}.{self.value}"


def not_service_error[V](error: ServiceError.OnSuccess[V]) -> TypeGuard[V]:
    return not isinstance(error, ServiceError)
