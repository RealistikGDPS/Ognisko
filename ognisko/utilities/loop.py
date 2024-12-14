from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def install_optimal_loop() -> None:
    if sys.platform in ("linux", "linux2", "darwin"):
        logger.debug(
            "Installing uvloop based on the OS platform.",
            extra={"platform": sys.platform},
        )
        import uvloop

        uvloop.install()
    elif sys.platform == "win32":
        logger.debug(
            "Installing winloop based on the OS platform.",
            extra={"platform": sys.platform},
        )
        import winloop

        winloop.install()

    else:
        logger.debug(
            "Falling back to the default asyncio event loop.",
            extra={"platform": sys.platform},
        )
