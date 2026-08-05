"""Tools: Export (export the raindrops of a collection to a file).

v1 endpoint:
  GET /raindrops/{collectionId}/export.{format}   export to CSV/HTML/ZIP - RAW bytes

Verified against the live API (it is missing from the official llms-full.txt, but
it works): .csv -> text/csv, .html -> text/html, .zip -> application/zip.
The result is written to disk, because the client returns bytes, not JSON.
"""
from __future__ import annotations

from pathlib import Path

from .. import config
from ..common import RaindropError, fmt, get_client, mcp

_DATA_DIR = config.PROJECT_ROOT / "data"


@mcp.tool()
def raindrop_export_collection(
    collection_id: int = 0,
    format: str = "csv",
    dest_path: str | None = None,
    search: str | None = None,
    sort: str = "-created",
) -> str:
    """Exports the raindrops of a collection to a file. GET /raindrops/{id}/export.{format}.

    Args:
        collection_id: Collection ID. 0 = all, -1 = Unsorted, -99 = Trash.
        format: "csv", "html" or "zip".
        dest_path: Destination file path. Omit for
            data/export-{collectionId}.{format} inside the server directory.
        search: Optional query narrowing the export (Raindrop operators).
        sort: Sort order ("-created" by default).
    """
    if format not in {"csv", "html", "zip"}:
        return 'Error: format must be "csv", "html" or "zip".'
    params: dict = {"sort": sort}
    if search:
        params["search"] = search
    try:
        content, ctype = get_client().download(
            f"/raindrops/{collection_id}/export.{format}", params=params
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    dest = Path(dest_path) if dest_path else _DATA_DIR / f"export-{collection_id}.{format}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return fmt({"saved": str(dest), "bytes": len(content), "content_type": ctype})
