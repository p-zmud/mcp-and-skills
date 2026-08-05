"""Tools: Tags.

v1 endpoints (collectionId is optional - omit it for every collection):
  GET    /tags/{collectionId}    tag list with counts
  PUT    /tags/{collectionId}    rename/merge: {tags:[...], replace:"new"}  (confirm when global)
  DELETE /tags/{collectionId}    remove tags: {tags:[...]}                  (confirm)

Rename = one tag in ``tags`` plus ``replace``. Merge = several tags in ``tags``
plus a single ``replace``.
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp, require_confirm


def _tags_path(collection_id: int | None) -> str:
    return f"/tags/{collection_id}" if collection_id is not None else "/tags"


@mcp.tool()
def raindrop_get_tags(collection_id: int | None = None) -> str:
    """Lists tags with their counts. GET /tags or /tags/{collectionId}.

    Args:
        collection_id: Narrow to one collection. Omit for tags across all of them.
    """
    try:
        data = get_client().call("GET", _tags_path(collection_id))
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_rename_tag(
    old_name: str, new_name: str, collection_id: int | None = None, confirm: bool = False
) -> str:
    """Renames a tag. PUT /tags/{collectionId} {tags:[old], replace:new}.

    Applies to every raindrop, or to one collection when you narrow it. With
    collection_id omitted the operation is GLOBAL and needs confirm=True.

    Args:
        old_name: Current tag name.
        new_name: New name.
        collection_id: Narrow to one collection. Omit for all of them (global, needs confirm).
        confirm: Required when collection_id is omitted.
    """
    if collection_id is None:
        warn = require_confirm(
            confirm, f"a global rename of tag '{old_name}' to '{new_name}'"
        )
        if warn:
            return warn
    try:
        data = get_client().call(
            "PUT", _tags_path(collection_id), json={"tags": [old_name], "replace": new_name}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_merge_tags(
    tags: list[str], into: str, collection_id: int | None = None, confirm: bool = False
) -> str:
    """Merges several tags into one. PUT /tags/{collectionId} {tags:[...], replace:into}.

    Args:
        tags: Tags to merge.
        into: Destination name (everything in ``tags`` takes this name).
        collection_id: Narrow to one collection. Omit for all of them (global, needs confirm).
        confirm: Required when collection_id is omitted.
    """
    if not tags:
        return "Error: pass a non-empty tags list."
    if collection_id is None:
        warn = require_confirm(confirm, f"a global merge of tags {tags} into '{into}'")
        if warn:
            return warn
    try:
        data = get_client().call(
            "PUT", _tags_path(collection_id), json={"tags": tags, "replace": into}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_remove_tags(
    tags: list[str], collection_id: int | None = None, confirm: bool = False
) -> str:
    """Removes tags from raindrops. DELETE /tags/{collectionId} {tags}. Needs confirm=True.

    Args:
        tags: Tags to remove (they vanish from the raindrops, the raindrops stay).
        collection_id: Narrow to one collection. Omit for every collection.
        confirm: Must be True.
    """
    if not tags:
        return "Error: pass a non-empty tags list."
    scope = "every collection" if collection_id is None else f"collection {collection_id}"
    warn = require_confirm(confirm, f"removing tags {tags} from {scope}")
    if warn:
        return warn
    try:
        data = get_client().call("DELETE", _tags_path(collection_id), json={"tags": tags})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
