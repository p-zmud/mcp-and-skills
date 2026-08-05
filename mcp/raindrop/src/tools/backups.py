"""Tools: Backups (whole-account backups).

v1 endpoints:
  GET /backups               list backups (id plus date)
  GET /backup                generate a new backup (emailed, asynchronous)
  GET /backup/{id}.{format}  download a backup (format: html | csv) - RAW bytes

A downloaded backup is written to disk, because the client returns bytes, not JSON.
"""
from __future__ import annotations

from pathlib import Path

from .. import config
from ..common import RaindropError, fmt, get_client, mcp

_DATA_DIR = config.PROJECT_ROOT / "data"


@mcp.tool()
def raindrop_list_backups() -> str:
    """Lists the available backups, newest first. GET /backups."""
    try:
        data = get_client().call("GET", "/backups")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_generate_backup() -> str:
    """Asks Raindrop to generate a new backup. GET /backup.

    Raindrop prepares the file asynchronously and emails it (how long depends on
    the number of bookmarks and the queue). It then shows up in
    raindrop_list_backups.
    """
    try:
        data = get_client().call("GET", "/backup")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data) if data else "Backup generation requested. The file arrives by email."


@mcp.tool()
def raindrop_download_backup(backup_id: str, format: str = "csv", dest_path: str | None = None) -> str:
    """Downloads a backup to disk. GET /backup/{id}.{format}.

    Args:
        backup_id: The backup _id (from raindrop_list_backups).
        format: "csv" or "html".
        dest_path: Destination file path. Omit for data/backup-{id}.{format} inside
            the server directory.
    """
    if format not in {"csv", "html"}:
        return 'Error: format must be "csv" or "html".'
    try:
        content, ctype = get_client().download(f"/backup/{backup_id}.{format}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    dest = Path(dest_path) if dest_path else _DATA_DIR / f"backup-{backup_id}.{format}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return fmt({"saved": str(dest), "bytes": len(content), "content_type": ctype})
