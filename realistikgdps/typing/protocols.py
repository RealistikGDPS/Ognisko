from typing import Protocol

class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...
