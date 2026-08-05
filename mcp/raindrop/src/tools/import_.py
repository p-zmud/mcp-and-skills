"""Tools: Import (URL metadata preview and duplicate checking).

v1 endpoints:
  GET  /import/url/parse?url=...   URL metadata (title, excerpt, media, type, meta)
  POST /import/url/exists          are these URLs already saved {urls:[...]} -> {ids:[...]}

Note: ``/import/url/exists`` returns {"result": false, "ids": []} when none of the
URLs exist, and that is a CORRECT response - the client does not treat it as an
error.
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp


@mcp.tool()
def raindrop_parse_url(url: str) -> str:
    """Fetches a URL's metadata without saving it. GET /import/url/parse.

    Returns title, excerpt, type, cover, media and meta (canonical, site, tags) -
    a preview of what Raindrop would store for that link.

    Args:
        url: URL to parse.
    """
    try:
        data = get_client().call("GET", "/import/url/parse", params={"url": url})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_check_urls_exist(urls: list[str]) -> str:
    """Checks which of the given URLs are already in the account. POST /import/url/exists.

    Args:
        urls: URLs to check.

    Returns {result, ids:[...]} where ids are the raindrops matching existing URLs
    (an empty list means none of them exist).
    """
    if not urls:
        return "Error: pass a non-empty urls list."
    try:
        data = get_client().call("POST", "/import/url/exists", json={"urls": urls})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
