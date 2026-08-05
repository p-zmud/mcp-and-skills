# mcp-and-skills

A Claude Code plugin marketplace: skills, subagents, hooks, MCP servers and CLI tools.

Everything listed in the marketplace installs directly in Claude Code.

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

### Hooks

Shell and Python hooks that fire on Claude Code events, before the tool call runs.

| Hook | What it does | Install |
| ---- | ------------ | ------- |
| [dash-guard](hooks/dash-guard) | Rewrites em and en dashes to a hyphen in `.md`, `.txt` and `.html` through `updatedInput`, so the write lands corrected on the first try instead of being denied and resent. Code blocks and inline code untouched | `/plugin install dash-guard@pzmud` |
| [big-read-guard](hooks/big-read-guard) | Denies a full `Read` of a text file over 32 KB - the biggest controllable context sink there is - and answers with the size, the token cost and the way out: Grep, then ranged reads. Images and PDFs exempt, explicit `offset`/`limit` passes | `/plugin install big-read-guard@pzmud` |

### MCP

Model Context Protocol servers exposing external APIs as tools.

| Server | What it does | Install |
| ------ | ------------ | ------- |
| [ksef](mcp/ksef) | KSeF API 2.0, the Polish national e-invoicing system: all 83 API operations in 54 tools - issuing and fetching invoices, metadata queries, permissions, certificates, tokens, QR codes, offline modes. Ships as a prebuilt `.mcpb` bundle for **Claude Desktop**, not as a Claude Code plugin. Entry docs are in Polish | download the [`.mcpb`](mcp/ksef) and double-click it |
| [raindrop](mcp/raindrop) | The whole Raindrop.io REST API v1 in 50 tools - collections, bookmarks, tags, highlights, filters, sharing, import, backups, export, covers, file upload - with a `confirm` guard on every irreversible, global or outbound operation | `/plugin install raindrop@pzmud` |

### CLI

Standalone command line tools, usually paired with a skill that teaches Claude to drive them.

| Tool | What it does | Install |
| ---- | ------------ | ------- |
| [ccswitch](cli/ccswitch) | Switches Claude Code accounts through `CLAUDE_CODE_OAUTH_TOKEN`, no Keychain, works headless - and handles the part that makes it hard: the `/login` credentials that override the token and come back every 8 hours. **Portfolio only** - code to read and copy, not a `/plugin install`, because it rewrites `~/.zshenv` and edits `~/.claude/.credentials.json` | read [the README](cli/ccswitch) first |
| [purelymail](cli/purelymail) | `pmail` - one stdlib-only Python CLI for both halves of Purelymail: read, search, send and reply over IMAP/SMTP, plus domains, mailboxes, aliases and app passwords over API v0 | `/plugin install purelymail@pzmud` |

## Repo layout

```
.claude-plugin/marketplace.json   registry - the single source of truth for /plugin
skills/<name>/                    one installable plugin per skill
agents/<name>/                    one installable plugin per subagent
hooks/<name>/                     one installable plugin per hook
mcp/<name>/                       one installable plugin per MCP server
cli/<name>/                       standalone CLI tool + its skill wrapper
docs/                             how to add an entry, plus copy-paste templates
```

Each `<name>/` directory is a self-contained Claude Code plugin: it holds its own
`.claude-plugin/plugin.json` and whatever it ships (`skills/`, `agents/`, `commands/`,
`hooks/`, `.mcp.json`, `scripts/`). Adding an entry means dropping in the directory and
registering it in `.claude-plugin/marketplace.json`.

See [docs/adding-an-entry.md](docs/adding-an-entry.md) for the full checklist.

## Disclaimer

Everything here is provided **as is, with no warranty and no support**, and you use it entirely
at your own risk. The author accepts no responsibility and no liability for any damage, data
loss, cost, downtime or other consequence of installing, running or modifying anything in this
repository.

Some entries do more than answer questions: hooks change what Claude Code is allowed to do,
`raindrop` writes to a live Raindrop.io account, and `ccswitch` rewrites `~/.zshenv` and edits
`~/.claude/.credentials.json`. Read an entry's README and its source before you run it, and keep
your own backups.

## License

MIT - see [LICENSE](LICENSE).
