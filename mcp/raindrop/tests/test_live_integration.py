"""Integration test against the LIVE API - a full lifecycle through the MCP tools only.

Safety rules for a real account:
- everything happens inside a freshly created throwaway collection,
- the collection and the raindrop are deleted in ``finally``, so cleanup runs
  even after a failure,
- global operations are NEVER touched (PUT /user, tag rename/merge/clean,
  collection merge, empty trash) - those are covered by the confirm guard test
  instead.

Skipped when RAINDROP_TOKEN is not set, so `pytest tests/` is green offline.
"""
from __future__ import annotations

import json
import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("RAINDROP_TOKEN"),
    reason="RAINDROP_TOKEN is not set - skipping the live test",
)


def _ok(out: str) -> dict:
    assert not out.startswith("Error:"), out
    return json.loads(out)


def test_full_lifecycle_through_tools(tmp_path):
    from src.tools import collections as col
    from src.tools import raindrops as rd
    from src.tools import highlights as hl
    from src.tools import filters as flt
    from src.tools import export as exp

    col_id = None
    rid = None
    try:
        # 1. create the throwaway collection
        c = _ok(col.raindrop_create_collection(title="ZZZ-pytest-DELETEME", view="list"))
        col_id = c["item"]["_id"]
        assert c["item"]["title"] == "ZZZ-pytest-DELETEME"

        # 2. create a raindrop inside it
        r = _ok(rd.raindrop_create(
            link="https://www.python.org/",
            title="pytest verify",
            tags=["pytest-verify"],
            collection_id=col_id,
            please_parse=False,
        ))
        rid = r["item"]["_id"]
        assert r["item"]["collection"]["$id"] == col_id

        # 3. update the raindrop
        u = _ok(rd.raindrop_update(rid, note="updated-by-test", important=True))
        assert u["item"]["note"] == "updated-by-test"
        assert u["item"]["important"] is True

        # 4. read it back
        g = _ok(rd.raindrop_get(rid))
        assert g["item"]["_id"] == rid

        # 5. highlight: add -> update -> remove
        a = _ok(hl.raindrop_add_highlight(rid, text="the Python language", color="red", note="n1"))
        hid = a["item"]["highlights"][0]["_id"]
        up = _ok(hl.raindrop_update_highlight(rid, hid, note="n2"))
        assert any(h["_id"] == hid and h["note"] == "n2" for h in up["item"]["highlights"])
        rm = _ok(hl.raindrop_remove_highlight(rid, hid, confirm=True))
        assert all(h["_id"] != hid for h in rm["item"].get("highlights", []))

        # 6. update_many with explicit ids (no confirm needed, because ids are given)
        um = _ok(rd.raindrop_update_many(col_id, ids=[rid], tags=["bulk-test"]))
        assert um.get("result") is True

        # 7. collection filters
        f = _ok(flt.raindrop_get_filters(col_id))
        assert "tags" in f

        # 8. export the collection to a temporary file
        dest = tmp_path / "export.csv"
        e = _ok(exp.raindrop_export_collection(col_id, format="csv", dest_path=str(dest)))
        assert dest.exists() and e["bytes"] > 0

        # 9. guard: update_many with no ids and no confirm has to be BLOCKED
        blocked = rd.raindrop_update_many(col_id, tags=["x"])
        assert "confirm=True" in blocked
    finally:
        # cleanup: delete the raindrop and the collection, then purge from Trash
        if rid is not None:
            rd.raindrop_remove(rid, confirm=True)
        if col_id is not None:
            col.raindrop_remove_collection(col_id, confirm=True)
        if rid is not None:
            rd.raindrop_remove_many(-99, ids=[rid], confirm=True)


def test_upload_file_and_cover():
    """Multipart upload (a file as a raindrop plus a cover) - throwaway, cleaned up in finally."""
    import base64

    from src.tools import collections as col
    from src.tools import files as fl
    from src.tools import raindrops as rd

    # the smallest valid 1x1 PNG
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    col_id = rid = None
    try:
        c = _ok(col.raindrop_create_collection(title="ZZZ-pytest-upload-DELETEME"))
        col_id = c["item"]["_id"]

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(png)
            path = tf.name
        try:
            up = _ok(fl.raindrop_upload_file(path, collection_id=col_id))
            rid = up["item"]["_id"]
            assert up["item"]["type"] == "image"

            cov = _ok(fl.raindrop_upload_cover(rid, path))
            assert cov.get("result") is True
        finally:
            os.unlink(path)
    finally:
        if rid is not None:
            rd.raindrop_remove(rid, confirm=True)
        if col_id is not None:
            col.raindrop_remove_collection(col_id, confirm=True)
        if rid is not None:
            rd.raindrop_remove_many(-99, ids=[rid], confirm=True)
