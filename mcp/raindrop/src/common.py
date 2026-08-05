"""The shared contract for the tool modules in src/tools/.

Every module imports ``mcp``, ``get_client``, ``fmt``, ``require_confirm`` and
``RaindropError`` from here, and registers its tools with the ``@mcp.tool()``
decorator. ``mcp_server.py`` imports the modules to load them (import equals
registration).

Tool contract:
- returns a ``str`` (JSON via ``fmt(...)`` or ``f"Error: {e}"``),
- destructive or global tools take ``confirm: bool = False`` and go through
  ``require_confirm``,
- one token (the test token), so no tool takes an account selector.
"""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from . import config
from .raindrop import RaindropClient, RaindropError  # noqa: F401 - re-exported for the modules

mcp = FastMCP("raindrop")


def get_client() -> RaindropClient:
    """An API client carrying the test token from the configuration."""
    return RaindropClient(config.get_token())


def fmt(data) -> str:
    """Serialises an API result to readable JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def require_confirm(confirm: bool, what: str) -> str | None:
    """Guardrail for destructive and global operations.

    Returns a warning message (a string) when ``confirm`` is falsy - the tool
    should return it immediately. Returns ``None`` when the operation may run.
    """
    if not confirm:
        return (
            f"This operation ({what}) is irreversible or global and needs confirmation. "
            f"Call it again with confirm=True if you are sure."
        )
    return None
