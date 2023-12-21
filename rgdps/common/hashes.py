from __future__ import annotations

import asyncio
import base64
import hashlib
import random
import string

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
        data=base64.urlsafe_b64decode(gjp.encode()),
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

    return base64.urlsafe_b64encode(xor_password).decode()


def encrypt_chests(response: str) -> str:
    return base64.urlsafe_b64encode(
        xor_cipher.cyclic_xor_unsafe(
            data=response.encode(),
            key=XorKeys.CHESTS,
        ),
    ).decode()


def encode_base64(data: str) -> str:
    return base64.urlsafe_b64encode(data.encode()).decode()


def decode_base64(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode()).decode()


CHARSET = string.ascii_letters + string.digits


def random_string(length: int) -> str:
    return "".join(random.choice(CHARSET) for _ in range(length))


def decrypt_chest_check(check_string: str) -> str:
    valid_check = check_string[5:]
    de_b64 = decode_base64(valid_check)

    return xor_cipher.cyclic_xor_unsafe(
        data=de_b64.encode(),
        key=XorKeys.CHESTS,
    ).decode()


def encrypt_message_content(content: str) -> str:
    return base64.urlsafe_b64encode(
        xor_cipher.cyclic_xor_unsafe(
            data=content.encode(),
            key=XorKeys.MESSAGE,
        ),
    ).decode()


def decrypt_message_content(content: str) -> str:
    de_b64 = decode_base64(content)

    return xor_cipher.cyclic_xor_unsafe(
        data=de_b64.encode(),
        key=XorKeys.MESSAGE,
    ).decode()


GJP2_PEPPER = "mI29fmAnxgTs"


def hash_gjp2(plain: str) -> str:
    return hashlib.sha1((plain + GJP2_PEPPER).encode()).hexdigest()
