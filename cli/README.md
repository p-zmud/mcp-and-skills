# CLI

One directory per command line tool. A tool ships as a plugin when it comes with a skill
that teaches Claude to drive it; otherwise it stays here as a plain standalone tool.

```
cli/<name>/
├── .claude-plugin/plugin.json   only if it is installable as a plugin
├── bin/<name>                   the executable
├── src/                         source, if larger than a single script
├── skills/<name>/SKILL.md       how and when Claude should use the tool
└── README.md                    install, configuration, usage examples
```

Every entry needs its own `README.md` with install steps and a runnable example, because
a CLI is also useful to a human reading the repo, not just to Claude.

Entries listed in `.claude-plugin/marketplace.json` are installable via `/plugin`;
entries that are not listed are portfolio only. Either way, add a row to the catalog
table in the root `README.md`.
