from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from . import leaderboards
from . import levels
from . import misc
from . import save_data
from . import user_comments
from . import users
from rgdps.config import config

router = APIRouter(
    prefix=config.http_url_prefix,
    default_response_class=PlainTextResponse,
)

router.add_api_route(
    "/accounts/registerGJAccount.php",
    users.register_post,
    methods=["POST"],
)

router.add_api_route(
    "/",
    misc.main_get,
)

router.add_api_route(
    "/getGJUserInfo20.php",
    users.user_info_get,
    methods=["POST"],
)

router.add_api_route(
    "/accounts/loginGJAccount.php",
    users.login_post,
    methods=["POST"],
)

router.add_api_route(
    "/updateGJUserScore22.php",
    users.user_info_update,
    methods=["POST"],
)

router.add_api_route(
    "/uploadGJAccComment20.php",
    user_comments.user_comments_post,
    methods=["POST"],
)

router.add_api_route(
    "/getGJAccountComments20.php",
    user_comments.user_comments_get,
    methods=["POST"],
)

# It may be possible to reuse `profiles.user_info_update`
router.add_api_route(
    "/updateGJAccSettings20.php",
    users.user_settings_update,
    methods=["POST"],
)

router.add_api_route(
    "/getGJSongInfo.php",
    levels.song_info_get,
    methods=["POST"],
)

# Geometry Dash forces these 2 to be prefixed with /database
router.add_api_route(
    "/database/accounts/syncGJAccountNew.php",
    save_data.save_data_get,
    methods=["POST"],
)

router.add_api_route(
    "/database/accounts/backupGJAccountNew.php",
    save_data.save_data_post,
    methods=["POST"],
)

router.add_api_route(
    "/getAccountURL.php",
    save_data.get_save_endpoint,
    methods=["POST"],
)

router.add_api_route(
    "/uploadGJLevel21.php",
    levels.level_post,
    methods=["POST"],
)

router.add_api_route(
    "/getGJLevels21.php",
    levels.levels_get,
    methods=["POST"],
)

router.add_api_route(
    "/downloadGJLevel22.php",
    levels.level_get,
    methods=["POST"],
)

router.add_api_route(
    "/getGJScores20.php",
    leaderboards.leaderboard_get,
    methods=["POST"],
)

router.add_api_route(
    "/likeGJItem211.php",
    user_comments.like_target_post,
    methods=["POST"],
)

router.add_api_route(
    "/deleteGJAccComment20.php",
    user_comments.user_comment_delete,
    methods=["POST"],
)
