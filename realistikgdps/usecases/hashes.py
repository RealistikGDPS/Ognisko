from __future__ import annotations

import asyncio

import bcrypt


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
