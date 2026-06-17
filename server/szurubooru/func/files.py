import os
from typing import Any, List, Optional
from szurubooru import config
from szurubooru.func import bunny
import logging
logger = logging.getLogger(__name__)


def _get_full_path(path: str) -> str:
    return os.path.join(config.config["data_dir"], path)


def delete(path: str) -> None:
    full_path = _get_full_path(path)
    logger.info("[FILES] delete called for: %s", path)

    if "bunny" in config.config:
        logger.info("[FILES] bunny delete called for: %s", path)
        bunny.delete(config.config, path)

    if os.path.exists(full_path):
        os.unlink(full_path)


def has(path: str) -> bool:
    return os.path.exists(_get_full_path(path))


def scan(path: str) -> List[Any]:
    if has(path):
        return list(os.scandir(_get_full_path(path)))
    return []


def move(source_path: str, target_path: str) -> None:
    os.rename(_get_full_path(source_path), _get_full_path(target_path))


def get(path: str) -> Optional[bytes]:
    full_path = _get_full_path(path)

    if os.path.exists(full_path):
        with open(full_path, "rb") as handle:
            return handle.read()

    return None


def save(path: str, content: bytes) -> None:
    full_path = _get_full_path(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as handle:
        handle.write(content)
    if path.startswith("temporary-uploads/"):
        return

    if "bunny" in config.config:
        bunny.upload(config.config, path, content)

