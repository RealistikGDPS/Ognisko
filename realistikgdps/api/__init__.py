from __future__ import annotations

from fastapi import APIRouter

from . import authentication
from . import misc
from realistikgdps.config import config

router = APIRouter(
    prefix=config.http_url_prefix,
)

router.add_api_route(
    "/registerGJAccount.php",
    authentication.register_post,
    methods=["POST"],
)

router.add_api_route(
    "/",
    misc.main_get,
)
