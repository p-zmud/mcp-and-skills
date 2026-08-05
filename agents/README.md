# Agents

One directory per subagent, each a self-contained Claude Code plugin.

```
agents/<name>/
├── .claude-plugin/plugin.json
└── agents/<name>.md      frontmatter: name, description, tools, model
```

The `description` decides when the main agent delegates, so state the trigger and what
the caller must pass in ("In the invocation provide ..."). Restrict `tools` to the
minimum the agent needs - a read-only reviewer should not get `Write` or `Edit`.

A plugin may ship several related agents; list them all under `agents` in `plugin.json`.

Register the directory in `.claude-plugin/marketplace.json` and add a row to the
catalog table in the root `README.md`.
