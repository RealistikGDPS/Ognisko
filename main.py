#!/usr/bin/env python3.9
from __future__ import annotations

import logging
import sys

import uvicorn

from realistikgdps import logger
from realistikgdps.config import config


def main() -> int:
    logger.init_logging(
        log_level=config.log_level,
    )

    # Uvloop does not work on windows. TODO: Maybe check for unix instead (would
    # require the same to be reflected in requirements)
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        if sys.platform != "win32":
            logger.warning("Uvloop has not been installed! This is a performance loss.")

    uvicorn.run(
        "realistikgdps.init_api:asgi_app",
        log_level=logging.WARNING,
        server_header=False,
        date_header=False,
        host=config.http_host,
        port=config.http_port,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
