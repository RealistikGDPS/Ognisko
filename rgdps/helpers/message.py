from __future__ import annotations

import base64

import xor_cipher

from rgdps.utilities import cryptography


MESSAGE_XOR_KEY = b"14251"

def encrypt_message_content(content: str) -> str:
    return base64.urlsafe_b64encode(
        xor_cipher.cyclic_xor_unsafe(
            data=content.encode(),
            key=MESSAGE_XOR_KEY,
        ),
    ).decode()


def decrypt_message_content(content: str) -> str:
    de_b64 = cryptography.decode_base64(content)

    return xor_cipher.cyclic_xor_unsafe(
        data=de_b64.encode(),
        key=MESSAGE_XOR_KEY,
    ).decode()

