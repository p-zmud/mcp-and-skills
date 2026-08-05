"""Tools: Files (upload a file as a raindrop, upload a cover).

v1 endpoints (multipart/form-data):
  PUT /raindrop/file        create a raindrop from a local file (the "file" field plus collectionId)
  PUT /raindrop/{id}/cover  set a raindrop's cover from a local file (the "cover" field)

Raindrop accepts images and PDFs as file raindrops, among others; the size limit
depends on the plan.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path

from .. import config
from ..common import RaindropError, fmt, get_client, mcp


def _open_file(path_str: str):
    p = Path(path_str).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"no such file: {p}")
    ctype = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    return p, ctype


@mcp.tool()
def raindrop_upload_file(file_path: str, collection_id: int = -1) -> str:
    """Creates a raindrop from a local file (image or PDF). PUT /raindrop/file.

    Args:
        file_path: Path to the file on disk.
        collection_id: Destination collection ID. Defaults to -1 (Unsorted).
    """
    try:
        p, ctype = _open_file(file_path)
        with p.open("rb") as fh:
            data = get_client().upload(
                "/raindrop/file",
                files={"file": (p.name, fh, ctype)},
                data={"collectionId": str(collection_id)},
            )
    except (RaindropError, config.ConfigError, FileNotFoundError, OSError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_upload_cover(raindrop_id: int, file_path: str) -> str:
    """Sets a raindrop's cover from a local file. PUT /raindrop/{id}/cover.

    Args:
        raindrop_id: Raindrop ID.
        file_path: Path to the image file on disk.
    """
    try:
        p, ctype = _open_file(file_path)
        with p.open("rb") as fh:
            data = get_client().upload(
                f"/raindrop/{raindrop_id}/cover",
                files={"cover": (p.name, fh, ctype)},
            )
    except (RaindropError, config.ConfigError, FileNotFoundError, OSError) as e:
        return f"Error: {e}"
    return fmt(data)
