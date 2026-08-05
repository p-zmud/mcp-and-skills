# MCP

One directory per MCP server, each a self-contained Claude Code plugin.

```
mcp/<name>/
├── .claude-plugin/plugin.json
├── .mcp.json             server definition (command/args/env, or a remote URL)
├── server/               optional - source, when the server lives in this repo
└── skills/<name>/        optional - skill teaching Claude the server's flow and gotchas
```

An entry may also ship a prebuilt `.mcpb` bundle instead of a plugin: that is the Claude Desktop
extension format, installed by double-clicking the file rather than through `/plugin`. Such an
entry stays out of `.claude-plugin/marketplace.json` and says so in its own `README.md`, because
`/plugin install` cannot do anything with it.

Never commit tokens. Reference them as `${VAR}` in `.mcp.json` and document the required
environment variables in the entry's own `README.md`, with an `.env.example` if useful.

If the server needs OAuth or a setup step, say so in the entry README - a server that
returns 401 out of the box is worse than no server.

Register the directory in `.claude-plugin/marketplace.json` and add a row to the
catalog table in the root `README.md`.
