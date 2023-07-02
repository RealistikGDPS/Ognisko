from __future__ import annotations

import asyncio
import base64
import hashlib

import bcrypt
import xor_cipher

from rgdps.constants.xor import XorKeys


def _compare_bcrypt(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_bcypt(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


async def compare_bcrypt(hashed: str, plain: str) -> bool:
    return await asyncio.to_thread(_compare_bcrypt, hashed, plain)


async def hash_bcypt_async(plain: str) -> str:
    """Hashes a plaintext password using bcrypt, running the hashing in an
    asynchronous thread.

    Args:
        plain (str): The plaintext password to hash.

    Returns:
        str: The bcrypt hash of the password.
    """

    return await asyncio.to_thread(hash_bcypt, plain)


def decode_gjp(gjp: str) -> str:
    """Decodes the "Geometry Jump Password" format into plaintext.

    Args:
        gjp (str): The encoded GJP string.

    Returns:
        str: The plaintext password.
    """

    return xor_cipher.cyclic_xor_unsafe(
        data=base64.b64decode(gjp.encode()),
        key=XorKeys.GJP,
    ).decode()


def hash_md5(plain: str) -> str:
    return hashlib.md5(plain.encode()).hexdigest()


def hash_sha1(plain: str) -> str:
    return hashlib.sha1(plain.encode()).hexdigest()


def hash_level_password(password: int) -> str:
    if not password:
        return "0"

    xor_password = xor_cipher.cyclic_xor_unsafe(
        data=str(password).encode(),
        key=XorKeys.LEVEL_PASSWORD,
    )

    return base64.b64encode(xor_password).decode()
