from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from . import authentication
from . import leaderboards
from . import levels
from . import misc
from . import profiles
from . import save_data
from . import user_comments
from rgdps.config import config

router = APIRouter(
    prefix=config.http_url_prefix,
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

router.add_api_route(
    "/updateGJUserScore22.php",
    profiles.update_user_info,
    methods=["POST"],
)

router.add_api_route(
    "/uploadGJAccComment20.php",
    user_comments.post_user_comment,
    methods=["POST"],
)

router.add_api_route(
    "/getGJAccountComments20.php",
    user_comments.view_user_comments,
    methods=["POST"],
)

# It may be possible to reuse `profiles.update_user_info`
router.add_api_route(
    "/updateGJAccSettings20.php",
    profiles.update_settings,
    methods=["POST"],
)

router.add_api_route(
    "/getGJSongInfo.php",
    levels.get_song_info,
    methods=["POST"],
)

# Geometry Dash forces these 2 to be prefixed with /database
router.add_api_route(
    "/database/accounts/syncGJAccountNew.php",
    save_data.load_save_data,
    methods=["POST"],
)

router.add_api_route(
    "/database/accounts/backupGJAccountNew.php",
    save_data.upload_save_data,
    methods=["POST"],
)

router.add_api_route(
    "/getAccountURL.php",
    save_data.get_save_endpoint,
    methods=["POST"],
)

router.add_api_route(
    "/uploadGJLevel21.php",
    levels.upload_level,
    methods=["POST"],
)

router.add_api_route(
    "/getGJLevels21.php",
    levels.search_levels,
    methods=["POST"],
)

router.add_api_route(
    "/downloadGJLevel22.php",
    levels.get_level,
    methods=["POST"],
)

router.add_api_route(
    "/getGJScores20.php",
    leaderboards.get_leaderboard,
    methods=["POST"],
)

router.add_api_route(
    "/likeGJItem211.php",
    user_comments.like_target,
    methods=["POST"],
)

router.add_api_route(
    "/deleteGJAccComment20.php",
    user_comments.delete_user_comment,
    methods=["POST"],
)