import time
from datetime import datetime, timezone
from typing import Dict
from szurubooru import config, rest
from szurubooru.func import posts, users, util

_featured_cache = None
_featured_cache_post_id = None
_featured_cache_post_version = None

@rest.routes.get("/info/?")
def get_info(ctx: rest.Context, _params: Dict[str, str] = {}) -> rest.Response:
    global _featured_cache, _featured_cache_post_id, _featured_cache_post_version

    ret = {
        "postCount": posts.get_post_count(),
        "serverTime": datetime.now(timezone.utc),
        "config": {
            "name": config.config["name"],
            "userNameRegex": config.config["user_name_regex"],
            "passwordRegex": config.config["password_regex"],
            "tagNameRegex": config.config["tag_name_regex"],
            "tagCategoryNameRegex": config.config["tag_category_name_regex"],
            "defaultUserRank": config.config["default_rank"],
            "enableSafety": config.config["enable_safety"],
            "contactEmail": config.config["contact_email"],
            "canSendMails": bool(config.config["smtp"]["host"]),
            "privileges": util.snake_case_to_lower_camel_case_keys(
                config.config["privileges"]
            ),
        },
        "featuredPost": None,
        "featuringUser": None,
        "featuringTime": None,
    }

    post_feature = posts.try_get_current_post_feature()
    current_post_id = post_feature.post_id if post_feature else None
    current_post_version = post_feature.post.version if post_feature else None

    if (
        _featured_cache is not None
        and current_post_id == _featured_cache_post_id
        and current_post_version == _featured_cache_post_version
    ):
        ret.update(_featured_cache)
        return ret

    if post_feature:
        _featured_cache = {
            "featuredPost": posts.serialize_post(post_feature.post, ctx.user),
            "featuringUser": users.serialize_user(post_feature.user, ctx.user),
            "featuringTime": post_feature.time,
        }
    else:
        _featured_cache = {
            "featuredPost": None,
            "featuringUser": None,
            "featuringTime": None,
        }

    _featured_cache_post_id = current_post_id
    _featured_cache_post_version = current_post_version

    ret.update(_featured_cache)
    return ret

