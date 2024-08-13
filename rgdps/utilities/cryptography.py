from __future__ import annotations

import asyncio
import base64
import hashlib
import random
import string

import bcrypt


def _compare_bcrypt(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_bcrypt(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


async def compare_bcrypt(hashed: str, plain: str) -> bool:
    return await asyncio.to_thread(_compare_bcrypt, hashed, plain)


async def hash_bcrypt_async(plain: str) -> str:
    return await asyncio.to_thread(hash_bcrypt, plain)


def hash_md5(plain: str) -> str:
    return hashlib.md5(plain.encode()).hexdigest()


def hash_sha1(plain: str) -> str:
    return hashlib.sha1(plain.encode()).hexdigest()


def encode_base64(data: str) -> str:
    return base64.urlsafe_b64encode(data.encode()).decode()


def decode_base64(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode()).decode()


CHARSET = string.ascii_letters + string.digits


def random_string(length: int) -> str:
    return "".join(random.choice(CHARSET) for _ in range(length))
