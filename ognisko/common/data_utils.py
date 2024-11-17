from __future__ import annotations

import random

from ognisko.common.typing import HasIntValue


def enum_int_list(l: list[HasIntValue]) -> list[int]:
    return [x.value for x in l]


def linear_biased_random[T](l: list[T]) -> T:
    q = len(l)
    return random.choices(l, weights=[q - i for i in range(q)])[0]
