from __future__ import annotations

from typing import Protocol


class HasIntValue(Protocol):
    @property
    def value(self) -> int:
        ...


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...
