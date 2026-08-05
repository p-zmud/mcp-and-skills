"""Tools: Filters (counters used to filter a collection).

v1 endpoint:
  GET /filters/{collectionId}   counts of tags, types, important, notes, highlights

Returns tags[], types[], created[], important, note, highlights, total, notag and
more. Useful for building a filter UI, or for a quick look at what a collection
actually holds.
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp


@mcp.tool()
def raindrop_get_filters(
    collection_id: int = 0, search: str | None = None, tags_sort: str = "-count"
) -> str:
    """Returns the filter counters for a collection. GET /filters/{collectionId}.

    Args:
        collection_id: Collection ID. 0 = all, -1 = Unsorted, -99 = Trash.
        search: Optional query narrowing the counters.
        tags_sort: Tag order: "-count" (by count, the default) or "_id" (alphabetical).
    """
    params: dict = {"tagsSort": tags_sort}
    if search:
        params["search"] = search
    try:
        data = get_client().call("GET", f"/filters/{collection_id}", params=params)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
