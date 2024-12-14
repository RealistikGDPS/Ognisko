#!/usr/bin/env python3.12
from __future__ import annotations

from ognisko.api import init_api
from ognisko.utilities import loop

loop.install_optimal_loop()
asgi_app = init_api()
