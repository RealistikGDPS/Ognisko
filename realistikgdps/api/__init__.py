from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from . import authentication
from . import misc
from . import profiles
from realistikgdps.config import config

router = APIRouter(
    prefix=config.http_url_prefix,
    # Required or else GD wont understand the response.
    default_response_class=PlainTextResponse,
)

router.add_api_route(
    "/accounts/registerGJAccount.php",
    authentication.register_post,
    methods=["POST"],
)

router.add_api_route(
    "/",
    misc.main_get,
)

router.add_api_route(
    "/getGJUserInfo20.php",
    profiles.view_user_info,
    methods=["POST"],
)

router.add_api_route(
    "/accounts/loginGJAccount.php",
    authentication.login_post,
    methods=["POST"],
)
