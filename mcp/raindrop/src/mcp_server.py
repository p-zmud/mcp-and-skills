"""Raindrop.io MCP server (FastMCP) - the entry point.

Run it by hand:  python -m src.mcp_server
Registering it in Claude Code: see README.md.

Architecture: a single `mcp` (src/common.py) with tools in src/tools/<group>.py.
Importing a module registers its tools, so every module is imported here.

Auth: the test token (RAINDROP_TOKEN) grants full access to your own account.
"""
from __future__ import annotations

from .common import mcp

# Importing a module registers its tools on the shared `mcp`. Order is irrelevant.
from .tools import (  # noqa: F401,E402
    user,
    collections,
    covers,
    sharing,
    raindrops,
    highlights,
    tags,
    filters,
    import_,
    backups,
    export,
    files,
)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
