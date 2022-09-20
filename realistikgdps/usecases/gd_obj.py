from __future__ import annotations

from realistikgdps.typing.protocols import SupportsStr


def into_gd_obj(obj: dict[SupportsStr, SupportsStr], sep: str = ":") -> str:
    return sep.join(str(key) + sep + str(value) for key, value in obj.items())
