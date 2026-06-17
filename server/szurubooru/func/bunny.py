import requests
import logging
logger = logging.getLogger(__name__)

def _base(config):
    zone = config["bunny"]["storage_zone"]
    base = config["bunny"].get("base_url", "https://storage.bunnycdn.com").rstrip("/")
    return f"{base}/{zone}"

def upload(config, path, content):
    url = _base(config) + "/" + path
    headers = {"AccessKey": config["bunny"]["api_key"]}
    logger.info(f"[BUNNY] Uploading: {url}")
    resp = requests.put(url, data=content, headers=headers)
    logger.info(f"[BUNNY] Status: {resp.status_code}")
    resp.raise_for_status()

def delete(config, path):
    url = _base(config) + "/" + path
    headers = {"AccessKey": config["bunny"]["api_key"]}
    logger.info(f"[BUNNY] Deleting: {url}")
    resp = requests.delete(url, headers=headers)
    logger.info(f"[BUNNY] Status: {resp.status_code}")
    if resp.status_code not in (200, 201, 204, 404):
        resp.raise_for_status()

def public_url(config, path, version):
    cdn = config["bunny"]["cdn_url"].rstrip("/")
    return f"{cdn}/{path}?v={version}"
