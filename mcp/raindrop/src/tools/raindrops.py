"""Tools: Raindrops (bookmarks).

v1 endpoints:
  GET    /raindrop/{id}              one raindrop
  GET    /raindrops/{collectionId}   list (search, sort, page, perpage, nested)
  POST   /raindrop                   create one
  POST   /raindrops                  create many {items:[...]}  (max 100)
  PUT    /raindrop/{id}              update one
  PUT    /raindrops/{collectionId}   update many {ids, ...}         (confirm when ids omitted)
  DELETE /raindrop/{id}              delete one (-> Trash)                     (confirm)
  DELETE /raindrops/{collectionId}   delete many {ids}; collId -99 = permanent (confirm)
  POST   /raindrop/suggest           suggestions for a new link {link}   (Pro -> 403 on free)
  GET    /raindrop/{id}/suggest      suggestions for an existing one     (Pro -> 403 on free)

System collection IDs: 0 = All, -1 = Unsorted, -99 = Trash.
Search uses Raindrop's own operators, for example #tag, type:article,
created:>2024-01-01.
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp, require_confirm


@mcp.tool()
def raindrop_get(raindrop_id: int) -> str:
    """One raindrop in full, highlights included. GET /raindrop/{id}."""
    try:
        data = get_client().call("GET", f"/raindrop/{raindrop_id}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_search(
    collection_id: int = 0,
    search: str | None = None,
    sort: str = "-created",
    page: int = 0,
    perpage: int = 25,
    nested: bool = False,
) -> str:
    """Lists or searches raindrops in a collection. GET /raindrops/{collectionId}.

    Args:
        collection_id: Collection ID. 0 = all, -1 = Unsorted, -99 = Trash.
        search: Query using Raindrop operators ("#tag", "type:article", a plain
            word, 'created:>2024-01-01', "match" and so on). Omit for everything
            in the collection.
        sort: "-created" (default), "created", "score", "-sort", "title",
            "-title", "domain", "-domain".
        page: Page number (0, 1, 2 ...).
        perpage: Items per page (max 50).
        nested: Whether to include raindrops from sub-collections.
    """
    params: dict = {"sort": sort, "page": page, "perpage": min(perpage, 50)}
    if search:
        params["search"] = search
    if nested:
        params["nested"] = "true"
    try:
        data = get_client().call("GET", f"/raindrops/{collection_id}", params=params)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_create(
    link: str,
    title: str | None = None,
    excerpt: str | None = None,
    note: str | None = None,
    tags: list[str] | None = None,
    collection_id: int | None = None,
    important: bool = False,
    cover_url: str | None = None,
    please_parse: bool = True,
) -> str:
    """Creates a raindrop (bookmark). POST /raindrop.

    Args:
        link: URL to save (required).
        title: Title. Omit it with please_parse=True and Raindrop fetches its own.
        excerpt: Short description or excerpt.
        note: A note.
        tags: List of tags.
        collection_id: Destination collection ID. Omit for Unsorted (-1).
        important: Mark as favourite (the star).
        cover_url: Cover URL.
        please_parse: True lets Raindrop pull metadata (title, cover, type).
    """
    body: dict = {"link": link, "important": important}
    if title is not None:
        body["title"] = title
    if excerpt is not None:
        body["excerpt"] = excerpt
    if note is not None:
        body["note"] = note
    if tags is not None:
        body["tags"] = tags
    if collection_id is not None:
        body["collection"] = {"$id": collection_id}
    if cover_url is not None:
        body["cover"] = cover_url
    if please_parse:
        body["pleaseParse"] = {}
    try:
        data = get_client().call("POST", "/raindrop", json=body)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_create_many(items: list[dict]) -> str:
    """Creates several raindrops at once (max 100). POST /raindrops.

    Args:
        items: List of raindrop objects. Each needs ``link``; optionally title,
            excerpt, note, tags, collection ({"$id": id}), important, cover,
            pleaseParse ({}). One element looks like:
            {"link": "https://x.com", "tags": ["a"], "collection": {"$id": 123}, "pleaseParse": {}}
    """
    if not items:
        return "Error: pass a non-empty items list."
    if len(items) > 100:
        return "Error: max 100 raindrops per request."
    try:
        data = get_client().call("POST", "/raindrops", json={"items": items})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_update(
    raindrop_id: int,
    title: str | None = None,
    excerpt: str | None = None,
    note: str | None = None,
    tags: list[str] | None = None,
    collection_id: int | None = None,
    important: bool | None = None,
    link: str | None = None,
    cover_url: str | None = None,
    order: int | None = None,
) -> str:
    """Updates a raindrop (only the fields you pass). PUT /raindrop/{id}.

    Args:
        raindrop_id: Raindrop ID.
        title/excerpt/note: Text fields.
        tags: The complete new tag list (it replaces the current one).
        collection_id: Moves the raindrop to another collection ({"$id": id}).
        important: Favourite (the star).
        link: Change the URL.
        cover_url: Cover URL.
        order: Sort position (0 = first).
    """
    body: dict = {}
    if title is not None:
        body["title"] = title
    if excerpt is not None:
        body["excerpt"] = excerpt
    if note is not None:
        body["note"] = note
    if tags is not None:
        body["tags"] = tags
    if collection_id is not None:
        body["collection"] = {"$id": collection_id}
    if important is not None:
        body["important"] = important
    if link is not None:
        body["link"] = link
    if cover_url is not None:
        body["cover"] = cover_url
    if order is not None:
        body["order"] = order
    if not body:
        return "Error: pass at least one field to change."
    try:
        data = get_client().call("PUT", f"/raindrop/{raindrop_id}", json=body)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_update_many(
    collection_id: int,
    ids: list[int] | None = None,
    tags: list[str] | None = None,
    important: bool | None = None,
    move_to_collection_id: int | None = None,
    cover_url: str | None = None,
    confirm: bool = False,
) -> str:
    """Bulk update of raindrops in a collection. PUT /raindrops/{collectionId}.

    With ``ids`` GIVEN it changes only those. With ``ids`` OMITTED it changes
    EVERY raindrop in the collection, and then it needs confirm=True.

    Args:
        collection_id: Collection ID (the scope of the operation).
        ids: The specific raindrops to change. Omit for all of them (dangerous).
        tags: New tag list for the selected raindrops.
        important: Set or clear the favourite flag.
        move_to_collection_id: Move the selected raindrops to another collection.
        cover_url: Set the cover ("<screenshot>" grabs a page screenshot).
        confirm: Required when ``ids`` is omitted (whole-collection operation).
    """
    body: dict = {}
    if ids is not None:
        body["ids"] = ids
    if tags is not None:
        body["tags"] = tags
    if important is not None:
        body["important"] = important
    if move_to_collection_id is not None:
        body["collection"] = {"$id": move_to_collection_id}
    if cover_url is not None:
        body["cover"] = cover_url
    if not body:
        return (
            "Error: pass at least one field to change "
            "(tags/important/move_to_collection_id/cover_url)."
        )
    if ids is None:
        warn = require_confirm(
            confirm, f"a bulk change to EVERY raindrop in collection {collection_id}"
        )
        if warn:
            return warn
    try:
        data = get_client().call("PUT", f"/raindrops/{collection_id}", json=body)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_remove(raindrop_id: int, confirm: bool = False) -> str:
    """Moves a raindrop to Trash (reversible). DELETE /raindrop/{id}. Needs confirm=True.

    Careful: if the raindrop is already in Trash (-99), the deletion is PERMANENT.
    """
    warn = require_confirm(confirm, f"deleting raindrop {raindrop_id} (to Trash)")
    if warn:
        return warn
    try:
        get_client().call("DELETE", f"/raindrop/{raindrop_id}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return f"Deleted raindrop {raindrop_id} (moved to Trash)."


@mcp.tool()
def raindrop_remove_many(collection_id: int, ids: list[int], confirm: bool = False) -> str:
    """Deletes several raindrops. DELETE /raindrops/{collectionId} {ids}. Needs confirm=True.

    Args:
        collection_id: Collection to delete from. CAREFUL: -99 (Trash) means a
            PERMANENT deletion.
        ids: Raindrop IDs to delete.
        confirm: Must be True.
    """
    if not ids:
        return "Error: pass a non-empty ids list."
    permanent = collection_id == -99
    warn = require_confirm(
        confirm,
        f"{'PERMANENTLY deleting' if permanent else 'moving to Trash'} {len(ids)} raindrops",
    )
    if warn:
        return warn
    try:
        data = get_client().call("DELETE", f"/raindrops/{collection_id}", json={"ids": ids})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_empty_trash(confirm: bool = False) -> str:
    """EMPTIES Trash - PERMANENTLY deletes every raindrop in it. DELETE /raindrops/-99.

    Irreversible and global - needs confirm=True.
    """
    warn = require_confirm(confirm, "permanently emptying the whole Trash")
    if warn:
        return warn
    try:
        data = get_client().call("DELETE", "/raindrops/-99")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_suggest_new(link: str) -> str:
    """Suggests a collection and tags for a NEW link. POST /raindrop/suggest {link}.

    A Pro feature - a free account gets HTTP 403.
    """
    try:
        data = get_client().call("POST", "/raindrop/suggest", json={"link": link})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}  (note: suggestions are a Pro feature, free accounts get 403)"
    return fmt(data)


@mcp.tool()
def raindrop_suggest_existing(raindrop_id: int) -> str:
    """Suggests a collection and tags for an EXISTING raindrop. GET /raindrop/{id}/suggest.

    A Pro feature - a free account gets HTTP 403.
    """
    try:
        data = get_client().call("GET", f"/raindrop/{raindrop_id}/suggest")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}  (note: suggestions are a Pro feature, free accounts get 403)"
    return fmt(data)
