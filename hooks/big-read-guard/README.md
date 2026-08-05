# big-read-guard

A `PreToolUse` hook on `Read`. It denies a full read of a text file larger than 32 KB and tells
Claude to `Grep` first, then read only the ranges it needs.

## Why

A full `Read` of a 25-80 KB source file costs roughly 6-20k tokens, and unlike a `Bash` result
you can ignore, those tokens sit in the context until the session ends. A handful of them turns
a long session into a short one. Nothing in Claude Code warns you: the read succeeds, the
context bill arrives later.

The guard does not forbid reading. It forbids reading *blind* - a full read with no idea what
is in the file. Grep first, then `offset`/`limit` on what matched.

## What it does

| Read call | Decision |
| --------- | -------- |
| text file over 32768 B, no `offset`/`limit` | **deny**, with a message naming the size in KB and the estimated token cost |
| same file with an explicit `offset` or `limit` | allow - the escape hatch |
| text file at or under 32768 B | allow |
| `.png .jpg .jpeg .gif .webp .bmp .tiff .tif .heic .svg` | allow |
| `.pdf` | allow |
| file missing, `file_path` missing, unparsable stdin, `jq` absent | allow (fail open) |

Images are out of scope on purpose: the API rescales them, so reading one costs about 1.5k
tokens no matter how large the file is. PDFs have their own `pages` parameter, which is already
the ranged read this guard is asking for.

The deny message is the useful half of the hook. It carries the size, the estimated token cost,
and the two ways forward (Grep plus ranges, or an explicit `limit` if you really want all of it),
so Claude reacts to the block instead of retrying it.

## Install

```bash
# inside Claude Code
/plugin marketplace add p-zmud/mcp-and-skills
/plugin install big-read-guard@pzmud
```

Or wire the script into your own `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [{"type": "command", "command": "/path/to/big-read-guard.sh", "timeout": 10}]
      }
    ]
  }
}
```

## Requirements

`bash` and [`jq`](https://jqlang.github.io/jq/) (`brew install jq`, `apt install jq`). Without
`jq` the hook exits 0 with no decision, so a missing dependency silently disables the guard
rather than breaking your session. Size lookup uses BSD `stat -f%z` and falls back to GNU
`stat -c%s`, so macOS and Linux both work.

## Tuning the threshold

The default is 32768 B, which is about 8k tokens - roughly the point where one file starts
crowding out everything else. Override it per shell:

```bash
export BIG_READ_GUARD_THRESHOLD=65536   # bytes
```

Anything non-numeric falls back to 32768 rather than erroring. The hook reads the variable from
the environment Claude Code was started in, so set it in your shell profile to make it stick.

## Fail open, deliberately

Every error path exits 0 with no decision: unparsable stdin, missing file, missing `jq`, a
`stat` that fails. A guard that breaks a session because its own dependency is missing costs
more than the tokens it saves. The one thing the hook is strict about is the size
check itself - that path has no fallback, it either denies or it does not.

## Tests

```bash
python3 tests/test_big_read_guard.py
```

19 tests over the whole contract: thresholds and their exact boundary, the image and PDF
exemptions, the `offset`/`limit` escape hatch, the `BIG_READ_GUARD_THRESHOLD` override
including a garbage value, every fail-open path, and the content of the deny message. All
fixtures are generated in a temp directory.

## License

MIT - see the [repository root](https://github.com/p-zmud/mcp-and-skills).
