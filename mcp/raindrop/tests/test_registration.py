"""Tests for tool registration on the MCP server - no network.

Importing src.mcp_server has to register the full set of tools, all of them
prefixed ``raindrop_``, and every destructive or global operation has to carry a
``confirm`` parameter.
"""
from __future__ import annotations

import asyncio

import pytest

from src import mcp_server  # noqa: F401 - the import is what registers the tools
from src.common import mcp


def _tools():
    return asyncio.run(mcp.list_tools())


def test_all_tools_registered():
    tools = _tools()
    # The count may grow - this pins the lower bound of full API coverage.
    assert len(tools) >= 45, f"too few tools: {len(tools)}"


def test_all_tools_have_prefix():
    for t in _tools():
        assert t.name.startswith("raindrop_"), t.name


def test_expected_tools_present():
    names = {t.name for t in _tools()}
    expected = {
        "raindrop_get_user", "raindrop_get_collections", "raindrop_create_collection",
        "raindrop_search", "raindrop_create", "raindrop_update", "raindrop_remove",
        "raindrop_get_tags", "raindrop_rename_tag", "raindrop_get_filters",
        "raindrop_add_highlight", "raindrop_get_all_highlights",
        "raindrop_parse_url", "raindrop_check_urls_exist",
        "raindrop_list_backups", "raindrop_export_collection",
        "raindrop_search_covers", "raindrop_share_collection",
        "raindrop_upload_file", "raindrop_suggest_new",
    }
    missing = expected - names
    assert not missing, f"missing tools: {missing}"


@pytest.mark.parametrize("name", [
    "raindrop_remove_collection", "raindrop_remove_collections",
    "raindrop_merge_collections", "raindrop_remove_empty_collections",
    "raindrop_reorder_collections", "raindrop_expand_collections",
    "raindrop_remove", "raindrop_remove_many", "raindrop_empty_trash",
    "raindrop_remove_highlight", "raindrop_remove_tags",
    "raindrop_remove_collaborator", "raindrop_share_collection",
    "raindrop_update_user",
])
def test_destructive_tools_require_confirm(name):
    tool = next(t for t in _tools() if t.name == name)
    props = tool.inputSchema.get("properties", {})
    assert "confirm" in props, f"{name} has no confirm guard"


def test_confirm_guard_blocks_without_confirm():
    # Calling a destructive tool without confirm must never reach the API.
    from src.tools.raindrops import raindrop_empty_trash
    out = raindrop_empty_trash(confirm=False)
    assert "needs confirmation" in out and "confirm=True" in out
