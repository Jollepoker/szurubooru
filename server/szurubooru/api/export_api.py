import json
import os
from typing import Dict
from szurubooru import rest, errors, config

JSONL_PATH = os.path.join(config.config["data_dir"], "posts.jsonl")

@rest.routes.get(r"/export/posts\.json/?")
def get_posts_json(
    ctx: rest.Context, _params: Dict[str, str] = {}
):
    if not os.path.exists(JSONL_PATH):
        raise errors.NotFound("Export file not found")

    posts = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                posts.append(json.loads(line))

    return posts
