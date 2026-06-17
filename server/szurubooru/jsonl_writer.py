from collections import deque
import fcntl
import json
import threading
import os
import time

from szurubooru import db, config
from szurubooru.func.posts import get_post_content_url
from szurubooru.model.post import Post

import logging
logger = logging.getLogger(__name__)

export_queue = deque()
queue_lock = threading.Lock()

INDEX_PATH = os.path.join(config.config["data_dir"], "posts.index.json")
JSONL_PATH = os.path.join(config.config["data_dir"], "posts.jsonl")
SKIP_TAGS = {"ai", "ai_generated"}

def atomic_write(path: str, write_fn):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            write_fn(f)
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    os.replace(tmp, path)

def load_index() -> dict:
    if not os.path.exists(INDEX_PATH):
        return {}
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(index: dict):
    def _write(f):
        data = json.dumps(index, ensure_ascii=False).encode("utf-8")
        f.write(data)
    atomic_write(INDEX_PATH, _write)

def start_export_thread():
    t = threading.Thread(target=export_thread, daemon=True)
    t.start()

def enqueue_export(post_id: int, action: str):
    with queue_lock:
        if (post_id, action) not in export_queue:
            export_queue.append((post_id, action))

def export_thread():
    while True:
        job = None

        with queue_lock:
            if export_queue:
                job = export_queue.popleft()

        if job is None:
            time.sleep(1)
            continue

        post_id, action = job
        if (post_id and action):
            try:
                patch_single_post(post_id, action)
            except Exception as e:
                logger.info("JSONL writer error: ", e)

def patch_single_post(post_id: int, action: str):
    with open(JSONL_PATH + ".lock", "w") as global_lock:
        fcntl.flock(global_lock, fcntl.LOCK_EX)

        index = load_index()

        if action != "delete":
            item = build_post_item(post_id)

            if item is None:
                action = "delete"
                new_line = None
                new_len = 0
            else:
                new_line = (json.dumps(item, ensure_ascii=False) + "\n").encode("utf-8")
                new_len = len(new_line)
        else:
            new_line = None
            new_len = 0

        entry = index.get(str(post_id))

        def write_temp(f_out):
            offset_map = {}
            current_offset = 0

            reverse_index = {v["offset"]: k for k, v in index.items()}

            if os.path.exists(JSONL_PATH):
                with open(JSONL_PATH, "rb") as f_in:
                    while True:
                        line_offset = f_in.tell()
                        line = f_in.readline()
                        if not line:
                            break

                        pid = reverse_index.get(line_offset)

                        if pid is None:
                            f_out.write(line)
                            current_offset += len(line)
                            continue

                        if int(pid) == post_id:
                            if action == "delete":
                                continue
                            else:
                                f_out.write(new_line)
                                offset_map[pid] = {
                                    "offset": current_offset,
                                    "length": new_len,
                                }
                                current_offset += new_len
                        else:
                            f_out.write(line)
                            offset_map[pid] = {
                                "offset": current_offset,
                                "length": len(line),
                            }
                            current_offset += len(line)

            if entry is None and action != "delete":
                f_out.write(new_line)
                offset_map[str(post_id)] = {
                    "offset": current_offset,
                    "length": new_len,
                }

            new_index = offset_map

            f_out._new_index = new_index

        tmp_path = JSONL_PATH + ".tmp"
        with open(tmp_path, "wb") as f_out:
            fcntl.flock(f_out, fcntl.LOCK_EX)
            write_temp(f_out)
            f_out.flush()
            os.fsync(f_out.fileno())
            new_index = getattr(f_out, "_new_index")
            fcntl.flock(f_out, fcntl.LOCK_UN)

        with open(JSONL_PATH, "a") as lockfile:
            fcntl.flock(lockfile, fcntl.LOCK_EX)
            os.replace(tmp_path, JSONL_PATH)
            fcntl.flock(lockfile, fcntl.LOCK_UN)

        save_index(new_index)

def rebuild_jsonl_files():
    with open(JSONL_PATH + ".lock", "w") as global_lock:
        fcntl.flock(global_lock, fcntl.LOCK_EX)

        all_posts = db.session.query(Post).all()

        index = {}
        offset = 0

        def write_jsonl(f):
            nonlocal offset
            for post in all_posts:
                item = build_post_item(post.post_id)
                if item is None:
                    continue
                line = (json.dumps(item, ensure_ascii=False) + "\n").encode("utf-8")
                length = len(line)

                f.write(line)
                index[str(post.post_id)] = {"offset": offset, "length": length}
                offset += length

        # Write JSONL atomically
        atomic_write(JSONL_PATH, write_jsonl)

        # Write index atomically
        save_index(index)

        logger.info(f"Rebuilt JSONL + index with {len(all_posts)} posts")

def get_post_content_type(tags):
    tag_names = {t.first_name.lower() for t in tags}

    if "meme" in tag_names or "memes" in tag_names:
        return "memes"
    if "edits" in tag_names or "edit" in tag_names:
        return "edits"
    return "art"

def build_post_item(post_id: int) -> dict:
    post = db.session.query(Post).get(post_id)
    if not post:
        raise ValueError(f"Post {post_id} not found")
    
    tag_names = {t.first_name.lower() for t in post.tags}
    if tag_names & SKIP_TAGS:
        return None

    slug = str(post.post_id)

    item = {
        "slug": slug,
        "status": "Live",
        "id": slug,
        "image": get_post_content_url(post),
        "content_type": get_post_content_type(post.tags),
        "safety_type": post.safety,
        "author": ", ".join(tag.first_name for tag in post.tags if tag.category.name == "artist") or "Unknown",
        "author_link": post.source or "",
        "date_created": post.creation_time.strftime("%m / %d / %Y"),
        "description": "Imported from https://booru.neppienep.info/post/" + slug + " list of tags: " + ", ".join(tag.first_name for tag in post.tags),
    }

    logger.info(f"JSONL built post item for post: {slug}")

    return item
