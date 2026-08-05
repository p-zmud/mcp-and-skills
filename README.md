# mcp-and-skills

A Claude Code plugin marketplace and portfolio: skills, subagents, MCP servers and CLI tools,
built and used in production on a 24/7 Mac Mini automation stack.

Everything here is installable directly in Claude Code.

## Install

```bash
# inside Claude Code
/plugin marketplace add p-zmud/mcp-and-skills
/plugin install <name>@pzmud
```

Then `/plugin` to browse, enable and disable entries.

## Catalog

### Skills

Reusable capabilities Claude loads on demand.

| Skill | What it does | Install |
| ----- | ------------ | ------- |

### Agents

Specialized subagents with their own tools and system prompt.

| Agent | What it does | Install |
| ----- | ------------ | ------- |
| [audytor-prawny-marketing](agents/audytor-prawny-marketing) | Audits content against Polish and EU law before it ships - ad disclosure, copyright and likeness, GDPR, terms of service, contests, regulated industries - and returns a verdict where every provision was opened in the run, not recalled. Agent output and entry docs are in Polish | `/plugin install audytor-prawny-marketing@pzmud` |

### MCP

Model Context Protocol servers exposing external APIs as tools.

| Server | What it does | Install |
| ------ | ------------ | ------- |

### CLI

Standalone command line tools, usually paired with a skill that teaches Claude to drive them.

| Tool | What it does | Install |
| ---- | ------------ | ------- |

## Repo layout

```
.claude-plugin/marketplace.json   registry - the single source of truth for /plugin
skills/<name>/                    one installable plugin per skill
agents/<name>/                    one installable plugin per subagent
mcp/<name>/                       one installable plugin per MCP server
cli/<name>/                       standalone CLI tool + its skill wrapper
docs/                             how to add an entry, plus copy-paste templates
```

Each `<name>/` directory is a self-contained Claude Code plugin: it holds its own
`.claude-plugin/plugin.json` and whatever it ships (`skills/`, `agents/`, `commands/`,
`hooks/`, `.mcp.json`, `scripts/`). Adding an entry means dropping in the directory and
registering it in `.claude-plugin/marketplace.json`.

See [docs/adding-an-entry.md](docs/adding-an-entry.md) for the full checklist.

## License

MIT - see [LICENSE](LICENSE).
