"""Tools: Highlights (selections inside a raindrop's content).

v1 endpoints:
  GET  /highlights                 every highlight (page, perpage)
  GET  /highlights/{collectionId}  highlights in a collection
  PUT  /raindrop/{id}              add, edit or remove a highlight (the highlights:[...] field)

A highlight object is {_id, text, color, note}. color: yellow (default), blue,
brown, cyan, gray, green, indigo, orange, pink, purple, red, teal.
Add    -> {"highlights":[{"text":..., "color":..., "note":...}]}
Edit   -> {"highlights":[{"_id":..., "<field>":...}]}
Remove -> {"highlights":[{"_id":..., "text":""}]}
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp, require_confirm


@mcp.tool()
def raindrop_get_all_highlights(page: int = 0, perpage: int = 25) -> str:
    """Lists every highlight the user has. GET /highlights.

    Args:
        page: Page number (0, 1, 2 ...).
        perpage: Items per page (max 50).
    """
    try:
        data = get_client().call(
            "GET", "/highlights", params={"page": page, "perpage": min(perpage, 50)}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_get_collection_highlights(collection_id: int, page: int = 0, perpage: int = 25) -> str:
    """Lists the highlights in one collection. GET /highlights/{collectionId}."""
    try:
        data = get_client().call(
            "GET", f"/highlights/{collection_id}", params={"page": page, "perpage": min(perpage, 50)}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_add_highlight(
    raindrop_id: int, text: str, color: str | None = None, note: str | None = None
) -> str:
    """Adds a highlight to a raindrop. PUT /raindrop/{id} (highlights:[{text,...}]).

    Args:
        raindrop_id: Raindrop ID.
        text: The text fragment to highlight (required).
        color: Colour (yellow/blue/brown/cyan/gray/green/indigo/orange/pink/purple/red/teal).
        note: A note attached to the highlight.
    """
    hl: dict = {"text": text}
    if color is not None:
        hl["color"] = color
    if note is not None:
        hl["note"] = note
    try:
        data = get_client().call("PUT", f"/raindrop/{raindrop_id}", json={"highlights": [hl]})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_update_highlight(
    raindrop_id: int,
    highlight_id: str,
    text: str | None = None,
    color: str | None = None,
    note: str | None = None,
) -> str:
    """Edits an existing highlight by _id. PUT /raindrop/{id} (highlights:[{_id,...}]).

    Args:
        raindrop_id: Raindrop ID.
        highlight_id: _id of the highlight to change.
        text: New text (CAREFUL: an empty string removes the highlight - use
            raindrop_remove_highlight for that).
        color: New colour.
        note: New note.
    """
    hl: dict = {"_id": highlight_id}
    if text is not None:
        hl["text"] = text
    if color is not None:
        hl["color"] = color
    if note is not None:
        hl["note"] = note
    if len(hl) == 1:
        return "Error: pass at least one field to change (text/color/note)."
    try:
        data = get_client().call("PUT", f"/raindrop/{raindrop_id}", json={"highlights": [hl]})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_remove_highlight(raindrop_id: int, highlight_id: str, confirm: bool = False) -> str:
    """Removes a highlight (sets text=""). PUT /raindrop/{id}. Needs confirm=True.

    Args:
        raindrop_id: Raindrop ID.
        highlight_id: _id of the highlight to remove.
        confirm: Must be True.
    """
    warn = require_confirm(
        confirm, f"removing highlight {highlight_id} from raindrop {raindrop_id}"
    )
    if warn:
        return warn
    try:
        data = get_client().call(
            "PUT", f"/raindrop/{raindrop_id}", json={"highlights": [{"_id": highlight_id, "text": ""}]}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
