"""Tools: User (the account and its settings).

v1 endpoints:
  GET  /user            the current user (full data plus config)
  GET  /user/{id}       another user's public data (numeric id; a name only
                        works when their profile is public, otherwise 404)
  PUT  /user            update account settings (GLOBAL, needs confirm)
"""
from __future__ import annotations

import json as _json

from .. import config
from ..common import RaindropError, fmt, get_client, mcp, require_confirm


@mcp.tool()
def raindrop_get_user() -> str:
    """Returns the current user (id, email, pro plan, groups, config). GET /user."""
    try:
        data = get_client().call("GET", "/user")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_get_user_public(user_id: str) -> str:
    """Another user's public data. GET /user/{id}.

    Args:
        user_id: Numeric user ID (for example "4049474"). A name only works when
            that user's profile is public, otherwise the API returns 404.
    """
    try:
        data = get_client().call("GET", f"/user/{user_id}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_update_user(
    full_name: str | None = None,
    config_json: str | None = None,
    confirm: bool = False,
) -> str:
    """Updates account settings. PUT /user. GLOBAL - needs confirm=True.

    Args:
        full_name: New display name (the fullName field).
        config_json: The config object as a JSON string (view settings and the
            like). The API merges it with the existing config.
        confirm: Must be True - this changes the real settings of your account.
    """
    body: dict = {}
    if full_name is not None:
        body["fullName"] = full_name
    if config_json is not None:
        try:
            body["config"] = _json.loads(config_json)
        except ValueError as e:
            return f"Error: config_json is not valid JSON: {e}"
    if not body:
        return "Error: pass at least one field to change (full_name/config_json)."
    warn = require_confirm(confirm, "changing account settings through PUT /user")
    if warn:
        return warn
    try:
        data = get_client().call("PUT", "/user", json=body)
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
