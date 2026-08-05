#!/bin/bash
# big-read-guard (PreToolUse Read): denies a full Read of a large TEXT file.
#
# A single full Read of a 25-80 KB source file is the largest controllable
# context eater in a session: roughly 6-20k tokens per call, and they stay in
# the context until the session ends. Images are OUT OF SCOPE - the API
# rescales them to ~1.5k tokens regardless of file size, so reading one is
# cheap. PDFs are out of scope too (they have their own `pages` parameter).
#
# Escape hatch: a Read with an explicit offset or limit passes untouched. The
# guard forces a deliberate choice (ranges after a Grep), it does not forbid
# reading.
#
# Errors are fail open (exit 0, no decision). Requires `jq`.
# Tests: python3 tests/test_big_read_guard.py
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE" ] && exit 0

LIMIT=$(echo "$INPUT" | jq -r '.tool_input.limit // empty' 2>/dev/null)
OFFSET=$(echo "$INPUT" | jq -r '.tool_input.offset // empty' 2>/dev/null)
if [ -n "$LIMIT" ] || [ -n "$OFFSET" ]; then exit 0; fi

# case-insensitive extension (bash 3.2 - no ${var,,})
EXT=$(printf '%s' "${FILE##*.}" | tr '[:upper:]' '[:lower:]')
case "$EXT" in
  png|jpg|jpeg|gif|webp|bmp|tiff|tif|heic|svg|pdf) exit 0 ;;
esac

# BSD stat (macOS) first, GNU coreutils as the fallback. Without the second
# form SIZE stays empty on Linux and the guard silently passes everything.
SIZE=$(stat -f%z "$FILE" 2>/dev/null)
case "$SIZE" in ''|*[!0-9]*) SIZE=$(stat -c%s "$FILE" 2>/dev/null) ;; esac
case "$SIZE" in ''|*[!0-9]*) exit 0 ;; esac

THRESHOLD=${BIG_READ_GUARD_THRESHOLD:-32768}
case "$THRESHOLD" in ''|*[!0-9]*) THRESHOLD=32768 ;; esac
[ "$SIZE" -le "$THRESHOLD" ] && exit 0

KB=$((SIZE / 1024))
TOK=$((SIZE / 4))
jq -cn --arg kb "$KB" --arg tok "$TOK" \
  '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:"big-read-guard: this file is \($kb) KB (~\($tok) tokens) - a full Read pulls all of it into the context for the rest of the session, which is the single largest token sink there is. Instead: Grep for the pattern, then Read only the ranges you need with offset/limit. A deliberate full read still works: pass an explicit limit and this guard stands down. Do not re-read a file you already have in context."}}' \
  2>/dev/null
exit 0
