from __future__ import annotations

from typing import Protocol
from typing import TypeGuard


class HasIntValue(Protocol):
    @property
    def value(self) -> int: ...


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


class Unset:
    """A type indicating an unset value (not to be mistaken with a `None`
    value).
    """

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "Unset"

    def __bool__(self) -> bool:
        return False


UNSET = Unset()


def is_set[T](value: T | Unset) -> TypeGuard[T]:
    return not isinstance(value, Unset)
