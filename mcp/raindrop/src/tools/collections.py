"""Tools: Collections (collections and folders).

v1 endpoints:
  GET    /collections              root collections (top level)
  GET    /collections/childrens    nested collections (children)
  POST   /collection               create
  GET    /collection/{id}          one collection
  PUT    /collection/{id}          update
  DELETE /collection/{id}          delete one (its raindrops go to Unsorted)
  DELETE /collections              delete many  {ids:[...]}                (confirm)
  PUT    /collections              reorder {sort:...} / expand {expanded:bool}  (confirm)
  PUT    /collections/merge        merge {to, ids:[...]}                   (confirm, global)
  PUT    /collections/clean        remove empty collections                (confirm, global)

System collection IDs: 0 = All, -1 = Unsorted, -99 = Trash.
view: "list" | "simple" | "grid" | "masonry".  parent: {"$id": parentId}.
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp, require_confirm


@mcp.tool()
def raindrop_get_collections() -> str:
    """Lists top level (root) collections. GET /collections."""
    try:
        data = get_client().call("GET", "/collections")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data.get("items", data) if isinstance(data, dict) else data)


@mcp.tool()
def raindrop_get_child_collections() -> str:
    """Lists nested collections (children, any depth). GET /collections/childrens."""
    try:
        data = get_client().call("GET", "/collections/childrens")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data.get("items", data) if isinstance(data, dict) else data)


@mcp.tool()
def raindrop_get_collection(collection_id: int) -> str:
    """One collection in full. GET /collection/{id}."""
    try:
        data = get_client().call("GET", f"/collection/{collection_id}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_create_collection(
    title: str,
    view: str = "list",
    public: bool = False,
    parent_id: int | None = None,
    sort: int | None = None,
    cover_url: str | None = None,
) -> str:
    """Creates a collection. POST /collection.

    Args:
        title: Collection name.
        view: View mode: "list" | "simple" | "grid" | "masonry".
        public: Whether it is publicly accessible.
        parent_id: Parent collection ID (nesting). Omit for a root collection.
        sort: Sort position (descending).
        cover_url: URL of the collection cover (icon).
    """
    body: dict = {"title": title, "view": view, "public": public}
    if parent_id is not None:
        body["parent"] = {"$id": parent_id}
    if sort is not None:
        body["sort"] = sort
    if cover_url is not None:
        body["cover"] = [cover_url]
    try:
        data = get_client().call("POST", "/collection", json=body)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_update_collection(
    collection_id: int,
    title: str | None = None,
    view: str | None = None,
    public: bool | None = None,
    parent_id: int | None = None,
    expanded: bool | None = None,
    sort: int | None = None,
    cover_url: str | None = None,
) -> str:
    """Updates a collection (only the fields you pass). PUT /collection/{id}.

    Args:
        collection_id: Collection ID.
        title: New name.
        view: View mode: "list" | "simple" | "grid" | "masonry".
        public: Public accessibility.
        parent_id: New parent (moves the collection). Moving a collection back to
            the root is not supported through this tool - do that in the UI.
        expanded: Whether sub-collections show expanded in the tree.
        sort: Sort position.
        cover_url: Cover URL.
    """
    body: dict = {}
    if title is not None:
        body["title"] = title
    if view is not None:
        body["view"] = view
    if public is not None:
        body["public"] = public
    if parent_id is not None:
        body["parent"] = {"$id": parent_id}
    if expanded is not None:
        body["expanded"] = expanded
    if sort is not None:
        body["sort"] = sort
    if cover_url is not None:
        body["cover"] = [cover_url]
    if not body:
        return "Error: pass at least one field to change."
    try:
        data = get_client().call("PUT", f"/collection/{collection_id}", json=body)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_remove_collection(collection_id: int, confirm: bool = False) -> str:
    """DELETES one collection (its raindrops move to Unsorted). DELETE /collection/{id}.

    Needs confirm=True.
    """
    warn = require_confirm(confirm, f"deleting collection {collection_id}")
    if warn:
        return warn
    try:
        get_client().call("DELETE", f"/collection/{collection_id}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return f"Deleted collection {collection_id} (its raindrops moved to Unsorted)."


@mcp.tool()
def raindrop_remove_collections(ids: list[int], confirm: bool = False) -> str:
    """DELETES several collections at once. DELETE /collections {ids}. Needs confirm=True.

    Args:
        ids: List of collection IDs to delete.
        confirm: Must be True.
    """
    if not ids:
        return "Error: pass a non-empty ids list."
    warn = require_confirm(confirm, f"deleting {len(ids)} collections")
    if warn:
        return warn
    try:
        data = get_client().call("DELETE", "/collections", json={"ids": ids})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_reorder_collections(sort: str, confirm: bool = False) -> str:
    """Sorts ALL collections by a key. PUT /collections {sort}. GLOBAL - needs confirm=True.

    Args:
        sort: "title" (A to Z), "-title" (Z to A) or "-count" (by raindrop count).
        confirm: Must be True - this reorders every collection you have.
    """
    if sort not in {"title", "-title", "-count"}:
        return 'Error: sort must be "title", "-title" or "-count".'
    warn = require_confirm(confirm, "reordering every collection")
    if warn:
        return warn
    try:
        data = get_client().call("PUT", "/collections", json={"sort": sort})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_expand_collections(expanded: bool, confirm: bool = False) -> str:
    """Expands or collapses ALL nested collections. PUT /collections {expanded}. confirm=True.

    Args:
        expanded: True expands every collection, False collapses every one.
        confirm: Must be True.
    """
    warn = require_confirm(
        confirm, f"{'expanding' if expanded else 'collapsing'} every collection"
    )
    if warn:
        return warn
    try:
        data = get_client().call("PUT", "/collections", json={"expanded": expanded})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_merge_collections(to: int, ids: list[int], confirm: bool = False) -> str:
    """Merges collections: moves raindrops from ``ids`` into ``to``. PUT /collections/merge.

    GLOBAL and irreversible - needs confirm=True.

    Args:
        to: ID of the destination collection (the one that survives).
        ids: Collections to merge in (they disappear, their raindrops land in ``to``).
        confirm: Must be True.
    """
    if not ids:
        return "Error: pass a non-empty ids list."
    warn = require_confirm(confirm, f"merging collections {ids} into {to}")
    if warn:
        return warn
    try:
        data = get_client().call("PUT", "/collections/merge", json={"to": to, "ids": ids})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_remove_empty_collections(confirm: bool = False) -> str:
    """Removes EVERY empty collection (count=0). PUT /collections/clean. GLOBAL - confirm=True."""
    warn = require_confirm(confirm, "removing every empty collection")
    if warn:
        return warn
    try:
        data = get_client().call("PUT", "/collections/clean")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
