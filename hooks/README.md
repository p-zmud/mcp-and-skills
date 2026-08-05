# Hooks

One directory per hook, each a self-contained Claude Code plugin.

```
hooks/<name>/
├── .claude-plugin/plugin.json
├── hooks/hooks.json          event, matcher, and the command to run
├── hooks/<name>.sh           the hook itself
├── tests/test_<name>.py      contract tests, runnable with no arguments
└── README.md                 what it blocks or rewrites, and how to tune it
```

Declare the manifest with `"hooks": "./hooks/hooks.json"` in `plugin.json`, and point every
command at `${CLAUDE_PLUGIN_ROOT}`. A hook installed as a plugin does not know where it landed
on disk, so a relative path or a `~/.claude/hooks/...` path is a bug that only shows up on
someone else's machine.

**A hook is fail open unless it is deliberately fail closed.** Missing `jq`, unparsable stdin,
a file that disappeared - all of those exit 0 with no decision and let the tool call through.
A hook that breaks a session because its own dependency is missing is worse than no hook.
Fail closed is a choice you make per hook, for the one case where letting the call through is
the actual damage, and then you say so in the entry README.

**Every hook ships tests of its contract**, because a hook has no visible failure mode: when it
silently stops firing, nothing in the session says so. Test the decision (`deny` / `updatedInput`
/ no output), the exit code, and the fail-open paths - not just the happy path. Tests run with
`python3 tests/test_<name>.py` and print `N/N PASS`.

Register the directory in `.claude-plugin/marketplace.json` and add a row to the catalog table
in the root `README.md`.
