# Skills

One directory per skill, each a self-contained Claude Code plugin.

```
skills/<name>/
├── .claude-plugin/plugin.json
└── skills/<name>/
    ├── SKILL.md          frontmatter: name, description (when to trigger)
    ├── references/       optional - docs loaded on demand
    └── scripts/          optional - helper scripts
```

The `description` in `SKILL.md` frontmatter is what makes Claude reach for the skill,
so write it as trigger conditions ("Use when the user ..."), not as a feature list.

Register the directory in `.claude-plugin/marketplace.json` and add a row to the
catalog table in the root `README.md`.
