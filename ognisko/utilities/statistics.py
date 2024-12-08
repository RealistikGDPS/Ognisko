from __future__ import annotations

import random


def linear_biased_random[T](l: list[T]) -> T:
    q = len(l)
    return random.choices(l, weights=[q - i for i in range(q)])[0]
