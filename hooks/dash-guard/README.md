# dash-guard

A `PreToolUse` hook on `Write|Edit`. It rewrites U+2014 (em dash) and U+2013 (en dash) to a plain
hyphen in prose files, **before the write lands**, and lets the write through.

## Why an autofix and not a denial

The obvious version of this rule is a guard that denies the write and tells the model to try
again. It works, and it is expensive: every denial costs a full retransmission of the content,
and long documents get retried several times. Running the original as a deny-style guard racked
up 187 denials in one session history.

`updatedInput` removes the retry entirely. The hook returns the corrected `tool_input`, Claude
Code writes that version, and the session moves on with a one-line note that the substitution
happened. Same outcome, one round trip, no content resent.

## What it does

| Write or Edit | Result |
| ------------- | ------ |
| `.md` | prose rewritten, fenced blocks and inline code left alone |
| `.txt`, `.html` | whole content rewritten |
| anything else (`.py`, `.json`, `.ts`, ...) | untouched |
| path matching `$DASH_GUARD_SKIP` | untouched |
| content with no long dashes | untouched, no output at all |
| unparsable stdin, missing `file_path`, missing `python3` | untouched (fail open) |

For `Edit`, only `new_string` is rewritten. `old_string` has to keep matching what is already on
disk, so touching it would break the edit.

Code and data are out of scope on purpose. In a fixture, a separator constant or a regex, a long
dash can be the data itself, and rewriting it silently is worse than not checking at all. In
Markdown the same logic applies one level down: fenced blocks and inline code are skipped, which
is why the documentation of this very rule can show the characters it removes.

## Install

```bash
# inside Claude Code
/plugin marketplace add p-zmud/mcp-and-skills
/plugin install dash-guard@pzmud
```

Or wire the dispatcher into your own `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "/path/to/dash-guard.sh", "timeout": 10}]
      }
    ]
  }
}
```

## Exempting verbatim material

Some prose must not be normalised: imported documents, quotes, interview transcripts, anything
you are storing exactly as received. `$DASH_GUARD_SKIP` holds colon-separated glob patterns
matched against the full file path.

```bash
export DASH_GUARD_SKIP='*/archive/*:*/quotes/*.md:*/transcripts/*'
```

Empty by default, so nothing is exempt until you say so. Patterns are matched with globbing
disabled during the split, so `*/archive/*` stays a pattern instead of expanding against your
current directory. The hook reads the variable from the environment Claude Code was started in.

## Requirements

`bash`, [`jq`](https://jqlang.github.io/jq/) and `python3` (3.6+, standard library only). If any
of them is missing the hook exits 0 with no output and the write goes through unchanged.

## Layout

```
hooks/dash-guard.sh    dispatcher: extension filter and $DASH_GUARD_SKIP
hooks/dash-guard.py    the transform: counts, rewrites, emits updatedInput
tests/test_dash_guard.py
```

The split is deliberate. Scope belongs in shell, where the hook contract already lives; the
Markdown-aware substitution belongs in Python, where a regex over fenced blocks is readable.

## Fail open, always

There is no deny path anywhere in this hook - not as a fallback, not for malformed input. A
typography rule that can block a write is a typography rule that will eventually block the wrong
write. Everything unexpected produces empty output, which Claude Code reads as "no opinion".

## Tests

```bash
python3 tests/test_dash_guard.py
```

27 tests. The transform half covers both dash characters, `Edit` versus `Write` payloads, fenced
blocks, inline code, an unclosed fence, a 500 KB document with a time budget, and the exact shape
of the response including the absence of `permissionDecision`. Payloads run in **both JSON
encodings**, escaped and raw UTF-8, because the escaped form is what `json.dumps` produces in a
test and the raw form is what actually arrives in production.

The dispatcher half covers the extension filter, `$DASH_GUARD_SKIP` matching and not matching,
a skip pattern that must not glob-expand against the current directory, paths with spaces, and
every fail-open path.

## License

MIT - see the [repository root](https://github.com/p-zmud/mcp-and-skills).
