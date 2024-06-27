from __future__ import annotations

import hashlib

GJP2_PEPPER = "mI29fmAnxgTs"


def hash_gjp2(plain: str) -> str:
    return hashlib.sha1((plain + GJP2_PEPPER).encode()).hexdigest()

