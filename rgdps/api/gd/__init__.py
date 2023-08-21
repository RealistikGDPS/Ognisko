from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import PlainTextResponse
from fastapi_limiter.depends import RateLimiter

from . import leaderboards
from . import level_comments
from . import levels
from . import misc
from . import save_data
from . import user_comments
from . import user_relationships
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
    dependencies=[
        Depends(RateLimiter(times=10, minutes=10)),
    ],
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
    "/getGJFriendRequests20.php",
    user_relationships.friend_requests_get,
    methods=["POST"],
)

router.add_api_route(
    "/uploadFriendRequest20.php",
    user_relationships.friend_request_upload,
    methods=["POST"],
    dependencies=[
        Depends(RateLimiter(times=1, seconds=30)),
    ],
)

router.add_api_route(
    "/readGJFriendRequest20.php",
    user_relationships.friend_request_read,
    methods=["POST"],
)

router.add_api_route(
    "/deleteGJFriendRequests20.php",
    user_relationships.friend_request_delete,
    methods=["POST"],
)

router.add_api_route(
    "/acceptGJFriendRequest20.php",
    user_relationships.friend_request_accept,
    methods=["POST"],
)

router.add_api_route(
    "/getGJUserList20.php",
    user_relationships.user_relatoionship_list_get,
    methods=["POST"],
)

router.add_api_route(
    "/removeGJFriend20.php",
    user_relationships.user_friend_remove,
    methods=["POST"],
)

router.add_api_route(
    "/blockGJUser20.php",
    user_relationships.block_user,
    methods=["POST"],
    dependencies=[
        Depends(RateLimiter(times=1, seconds=30)),
    ],
)

router.add_api_route(
    "/unblockGJUser20.php",
    user_relationships.unblock_user,
    methods=["POST"],
)

router.add_api_route(
    "/uploadGJAccComment20.php",
    user_comments.user_comments_post,
    methods=["POST"],
    dependencies=[
        Depends(RateLimiter(times=4, minutes=1)),
    ],
)

router.add_api_route(
    "/getGJAccountComments20.php",
    user_comments.user_comments_get,
    methods=["POST"],
)

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
    dependencies=[
        Depends(RateLimiter(times=1, minutes=5)),
    ],
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
    # TODO: Tweak based on average user behaviour. May be way too high.
    dependencies=[
        Depends(RateLimiter(times=3, minutes=10)),
    ],
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
    # TODO: Tweak based on average user behaviour. May be too low.
    dependencies=[
        Depends(RateLimiter(times=100, minutes=10)),
    ],
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
    dependencies=[
        Depends(RateLimiter(times=50, minutes=10)),
    ],
)

router.add_api_route(
    "/deleteGJAccComment20.php",
    user_comments.user_comment_delete,
    methods=["POST"],
)

router.add_api_route(
    "/uploadGJComment21.php",
    level_comments.create_comment_post,
    methods=["POST"],
    dependencies=[
        Depends(RateLimiter(times=4, minutes=1)),
    ],
)

router.add_api_route(
    "/requestUserAccess.php",
    users.request_status_get,
    methods=["POST"],
)

router.add_api_route(
    "/getGJComments21.php",
    level_comments.level_comments_get,
    methods=["POST"],
)

router.add_api_route(
    "/suggestGJStars20.php",
    levels.suggest_level_stars,
    methods=["POST"],
)

router.add_api_route(
    "/getGJCommentHistory.php",
    level_comments.comment_history_get,
    methods=["POST"],
)

router.add_api_route(
    "/deleteGJComment20.php",
    level_comments.level_comment_delete,
    methods=["POST"],
)
