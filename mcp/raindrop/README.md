# raindrop

An MCP server (stdio, FastMCP) for [Raindrop.io](https://raindrop.io), covering the whole REST
API v1 in **50 tools**: collections, bookmarks, tags, highlights, filters, sharing, import,
backups, export, covers, file upload and the account itself.

Not a subset. If the v1 API can do it, there is a tool for it.

## Install

```bash
# inside Claude Code
/plugin marketplace add p-zmud/mcp-and-skills
/plugin install raindrop@pzmud
```

The bundled `.mcp.json` launches the server with [`uv`](https://docs.astral.sh/uv/), which
resolves the three dependencies into a throwaway environment on first run:

```json
{
  "command": "uv",
  "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}",
           "--with", "mcp>=1.2,<2", "--with", "requests", "--with", "python-dotenv",
           "python", "-m", "src.mcp_server"],
  "env": {"RAINDROP_TOKEN": "${RAINDROP_TOKEN}"}
}
```

The working directory is set with uv's `--directory`, not with a `cwd` key. `${CLAUDE_PLUGIN_ROOT}`
is expanded inside `args`, so the server starts wherever the plugin landed; a `cwd` field is left
unexpanded and the server dies with `No module named 'src'`.

**No `uv`?** Then either install it (`brew install uv`, or `curl -LsSf https://astral.sh/uv/install.sh | sh`),
or run the server from a virtualenv and register it by hand:

```bash
git clone https://github.com/p-zmud/mcp-and-skills.git
cd mcp-and-skills/mcp/raindrop
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

claude mcp add raindrop -s user -e RAINDROP_TOKEN=... \
  -- "$PWD/.venv/bin/python" -m src.mcp_server
```

`mcp` is pinned below 2.0 on purpose: `mcp.server.fastmcp` was removed in 2.0, and an
unconstrained `--with mcp` installs a version this server cannot import.

## The token

Raindrop calls it a **test token**: a permanent token for your own account, minted at
[app.raindrop.io/settings/integrations](https://app.raindrop.io/settings/integrations) - create an
app, then copy "Test token" from its page.

```bash
export RAINDROP_TOKEN=...        # in your shell profile, so Claude Code inherits it
```

Locally you can instead drop a `.env` file next to `src/` with `RAINDROP_TOKEN=...`; it is loaded
regardless of the working directory and it is gitignored. A missing token does not stop the
server from starting - tools register fine, and the first call returns a message telling you
where to get one.

**OAuth is deliberately left out.** Raindrop's OAuth has no granular scopes: access is
all-or-nothing, so an OAuth token grants exactly what a test token already grants. The only thing
it would add is multiple accounts, at the cost of a callback server, a token store and a refresh
loop. This server serves one account, so it takes the token and skips all of that.
`RAINDROP_CLIENT_ID`/`RAINDROP_CLIENT_SECRET` are still read from the environment, in case that
ever changes.

## The 50 tools

| Group | Tools |
| ----- | ----- |
| **Account** (3) | `get_user`, `get_user_public`, `update_user` |
| **Collections** (11) | `get_collections`, `get_child_collections`, `get_collection`, `create_collection`, `update_collection`, `remove_collection`, `remove_collections`, `reorder_collections`, `expand_collections`, `merge_collections`, `remove_empty_collections` |
| **Raindrops** (11) | `get`, `search`, `create`, `create_many`, `update`, `update_many`, `remove`, `remove_many`, `empty_trash`, `suggest_new`, `suggest_existing` |
| **Highlights** (5) | `get_all_highlights`, `get_collection_highlights`, `add_highlight`, `update_highlight`, `remove_highlight` |
| **Sharing** (5) | `share_collection`, `get_collaborators`, `change_collaborator`, `remove_collaborator`, `accept_invitation` |
| **Tags** (4) | `get_tags`, `rename_tag`, `merge_tags`, `remove_tags` |
| **Backups** (3) | `list_backups`, `generate_backup`, `download_backup` |
| **Covers** (2) | `search_covers`, `get_featured_covers` |
| **Import** (2) | `parse_url`, `check_urls_exist` |
| **Files** (2) | `upload_file`, `upload_cover` |
| **Filters** (1) | `get_filters` |
| **Export** (1) | `export_collection` |

Every tool is prefixed `raindrop_`, so the table drops the prefix for readability:
`raindrop_search`, `raindrop_get_user` and so on.

## The confirm guard

Anything irreversible, global or outbound takes `confirm: bool = False` and refuses to run
without it, returning a message that names what would happen. That covers `remove_*`,
`merge_*`, `empty_trash`, `reorder_collections`, `expand_collections`, global tag
`rename`/`merge`/`remove`, `update_user`, and `share_collection` (which sends real email to real
people).

The guard exists because an MCP tool is called by a model, and "delete every empty collection"
is one plausible tool call away from a bad afternoon. `raindrop_update_many` shows the pattern
best: with an explicit `ids` list it just runs, and with `ids` omitted (meaning every raindrop in
the collection) it demands `confirm=True`.

## Gotchas the client already handles

- **`result:false` is not always an error.** The client only raises when `result` is false AND an
  `errorMessage` is present, because `import/url/exists` answers `{"result": false, "ids": []}`
  when nothing matched, which is a correct response.
- **Export and backup return raw bytes** (CSV/HTML/ZIP), not JSON, so those tools write a file
  and return its path. Without `dest_path` they write to `data/` inside the server directory.
- **Suggestions are a Pro feature.** `raindrop_suggest_new` and `raindrop_suggest_existing`
  return HTTP 403 on a free account, and say so in the error rather than failing mysteriously.
- **`GET /user/{id}` wants a numeric ID.** A username only resolves when that profile is public.
- **System collection IDs:** `0` = all, `-1` = Unsorted, `-99` = Trash. Deleting from `-99` is
  permanent, and the tool says so before asking for `confirm`.
- **Rate limit is about 120 req/min**, so 429 and 5xx are retried with exponential backoff and
  the client honours `Retry-After`.

## Layout

```
.mcp.json              the server definition Claude Code reads
src/config.py          .env plus token plus API_BASE
src/raindrop.py        the thin client: call() JSON, download() bytes, upload() multipart
src/common.py          mcp = FastMCP("raindrop"), get_client(), fmt(), require_confirm()
src/tools/*.py         12 modules, one per resource group - importing one registers its tools
src/mcp_server.py      imports every tools module and calls mcp.run()
tests/
```

Adding a tool means writing one `@mcp.tool()` function in the right `src/tools/<group>.py`,
going through `get_client().call(method, path, params=, json=)`, and returning `fmt(data)` or
`f"Error: {e}"`. A new module needs one import line in `src/mcp_server.py`.

## Tests

```bash
pytest tests/
```

26 offline tests, plus 2 live ones that skip themselves unless `RAINDROP_TOKEN` is set.

- `test_client.py` pins the client's gotchas with a fake session: `result:false` with and without
  an `errorMessage`, a retried 429, exhausted retries, an empty body, a raw download.
- `test_registration.py` asserts that importing the server registers the full tool set, that
  every name carries the `raindrop_` prefix, and that all 14 destructive tools expose `confirm`.
- `test_live_integration.py` runs a full lifecycle against the real API through the tools
  themselves: create a throwaway collection, create and update a raindrop, add, edit and remove a
  highlight, bulk update, read filters, export to a temp file, and confirm the guard blocks an
  unconfirmed bulk write. Everything is deleted in `finally`, including a purge from Trash, and
  it never touches a global operation.

## License

MIT - see the [repository root](https://github.com/p-zmud/mcp-and-skills).
