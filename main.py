#!/usr/bin/env python3.9
from __future__ import annotations

import logging
import sys

import uvicorn
import uvloop

from realistikgdps.config import config


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
    )

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
