from __future__ import annotations

from ognisko import settings


async def main_get() -> str:
    return f"{settings.OGNISKO_PRODUCT_NAME} - Powered by RealistikGDPS"
