# Adding an entry

Every entry is a directory under `skills/`, `agents/`, `mcp/` or `cli/`, and every
installable entry is a Claude Code plugin: a directory with `.claude-plugin/plugin.json`
at its root plus the components it ships.

## Checklist

1. **Pick the category and name.** Lowercase, kebab-case, unique across the whole repo -
   the name is what people type in `/plugin install <name>@pzmud`.
2. **Create the directory** from the matching layout in the category `README.md`, using
   the templates in [templates/](templates/).
3. **Fill `plugin.json`.** `name` must match the directory name. Bump `version` on every
   change that users would notice.
4. **Strip secrets.** No tokens, no absolute paths from a private machine, no client
   data. Environment variables go in as `${VAR}` and get documented in the entry README.
5. **Register it** in `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "<name>",
     "source": "./skills/<name>",
     "description": "One line, what it does and when to use it",
     "category": "skills",
     "keywords": ["...", "..."]
   }
   ```

   `source` is the path relative to the repo root, so the category directory is part of it.
6. **Add a catalog row** to the root `README.md` under the right section.
7. **Test the install end to end** before pushing:

   ```bash
   claude plugin marketplace add /absolute/path/to/mcp-and-skills   # local checkout
   claude plugin install <name>@pzmud
   ```

   Then start Claude Code and confirm the skill triggers, the agent is listed, or the MCP
   server connects. An entry that installs but does nothing is not done.

   Afterwards `claude plugin marketplace remove pzmud` - the local checkout and the
   published repo register under the same name and cannot coexist.
8. **Commit and push.** One entry per commit, message `add <category>/<name>`.

## Component reference

| Component | Where it lives | Declared in `plugin.json` |
| --------- | -------------- | ------------------------- |
| Skill | `skills/<name>/SKILL.md` | auto-discovered |
| Agent | `agents/<name>.md` | `"agents": ["./agents/<name>.md"]` |
| Command | `commands/<name>.md` | `"commands": ["./commands/<name>.md"]` |
| Hook | `hooks/hooks.json` | `"hooks": "./hooks/hooks.json"` |
| MCP server | `.mcp.json` | auto-discovered |

Paths inside a plugin are relative to the plugin root and can use `${CLAUDE_PLUGIN_ROOT}`
when a script needs an absolute path at runtime.

## Quality bar

An entry belongs in this repo when it is:

- **Actually used** - it solves a real problem, not a demo.
- **Self-contained** - installs and runs without hidden setup outside its own README.
- **Loud on failure** - no silent fallbacks, no swallowed errors.
- **Small** - the simplest thing that works, no speculative configurability.
