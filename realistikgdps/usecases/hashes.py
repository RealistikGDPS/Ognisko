from __future__ import annotations

import asyncio
import base64

import bcrypt
import xor_cipher

from realistikgdps.constants.xor import XorKeys


def compare_bcrypt(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def compare_bcrypt_async(hashed: str, plain: str) -> bool:
    """Compares a bcrypt hash with a plaintext password, running the comparison
    in an asynchronous thread.

    Args:
        hashed (str): The bcrypt has of the password.
        plain (str): The plaintext password to compare it to.

    Returns:
        bool: Whether the password matches the hash.
    """

    return await asyncio.to_thread(compare_bcrypt, hashed, plain)


def decode_gjp(gjp: str) -> str:
    """Decodes the "Geometry Jump Password" format into plaintext.

    Args:
        gjp (str): The encoded GJP string.

    Returns:
        str: The plaintext password.
    """

    return xor_cipher.xor_cyclic(
        content=base64.b64decode(gjp.encode()),
        key=XorKeys.GJP,
    ).decode()
