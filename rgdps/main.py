#!/usr/bin/env python3.10
from __future__ import annotations

import sys

from rgdps import logger
from rgdps.api import init_api
from rgdps.config import config

# Uvloop does not work on windows. TODO: Maybe check for unix instead (would
# require the same to be reflected in requirements)
try:
    import uvloop  # type: ignore

    uvloop.install()
except ModuleNotFoundError:
    if sys.platform != "win32":
        logger.warning("Uvloop has not been installed! This is a performance loss.")


asgi_app = init_api()
