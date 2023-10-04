#!/usr/bin/env python3.10
from __future__ import annotations

import sys

from rgdps.api import init_api

if sys.platform != "win32":
    import uvloop

    uvloop.install()
else:
    import winloop

    winloop.install()


asgi_app = init_api()
