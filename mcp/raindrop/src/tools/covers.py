"""Tools: Covers and icons for collections.

v1 endpoints:
  GET /collections/covers/{text}   search icons by keyword
  GET /collections/covers          featured covers

Returns items[] of {title, icons:[{png?, svg?}]}. Use an icon URL as cover_url in
raindrop_create_collection or raindrop_update_collection.
"""
from __future__ import annotations

import urllib.parse

from .. import config
from ..common import RaindropError, fmt, get_client, mcp


@mcp.tool()
def raindrop_search_covers(text: str) -> str:
    """Searches collection icons and covers by keyword. GET /collections/covers/{text}.

    Args:
        text: Keyword (for example "book", "code", "music").
    """
    try:
        data = get_client().call("GET", f"/collections/covers/{urllib.parse.quote(text)}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_get_featured_covers() -> str:
    """Returns the featured collection covers. GET /collections/covers."""
    try:
        data = get_client().call("GET", "/collections/covers")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
