#!/usr/bin/env python3.12
from __future__ import annotations

import sys

import ddtrace

from rgdps.api import init_api

if sys.platform != "win32":
    import uvloop

    uvloop.install()
else:
    import winloop

    winloop.install()


ddtrace.patch_all()
asgi_app = init_api()
