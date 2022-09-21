from __future__ import annotations

from typing import Union

from realistikgdps.typing.types import GDSerialisable


def into_gd_obj(obj: GDSerialisable, sep: str = ":") -> str:
    return sep.join(str(key) + sep + str(value) for key, value in obj.items())
