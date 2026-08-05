"""Configuration for the Raindrop.io MCP server.

Auth: a **test token** (``RAINDROP_TOKEN``), a permanent token granting access to
your ENTIRE own account. Raindrop's OAuth has no granular scopes (access is
all-or-nothing), so a test token is effectively "every scope" for your own
account. Multi-account OAuth (``RAINDROP_CLIENT_ID``/``SECRET``) is deliberately
left out - see the README. The values are still read from the environment in
case it is ever needed.

Configuration comes from the environment or from a ``.env`` file in the project
directory (loaded regardless of the current working directory). Missing
configuration does NOT stop the server from starting - validation happens when a
tool is called, so that tool registration works without a token.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from the project directory regardless of cwd.
load_dotenv(PROJECT_ROOT / ".env")

# --- REST API ---------------------------------------------------------------
API_BASE = "https://api.raindrop.io/rest/v1"


class ConfigError(RuntimeError):
    """Missing or invalid configuration."""


def get_token() -> str:
    """The test token from the environment or `.env`, or a ConfigError with instructions."""
    tok = os.environ.get("RAINDROP_TOKEN", "").strip()
    if not tok:
        raise ConfigError(
            "RAINDROP_TOKEN is not set. Go to https://app.raindrop.io/settings/integrations, "
            "create an app, copy its 'Test token' and either export it or put it in a .env "
            f"file in {PROJECT_ROOT} as RAINDROP_TOKEN=..."
        )
    return tok


def oauth_credentials() -> tuple[str, str] | None:
    """(client_id, client_secret) if both are set, otherwise None. Currently unused."""
    cid = os.environ.get("RAINDROP_CLIENT_ID", "").strip()
    secret = os.environ.get("RAINDROP_CLIENT_SECRET", "").strip()
    return (cid, secret) if cid and secret else None
