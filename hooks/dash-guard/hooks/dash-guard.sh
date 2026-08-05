#!/bin/bash
# dash-guard (PreToolUse Write|Edit): dispatcher.
#
# Decides WHETHER dash-guard.py gets to see the payload. Prose files only
# (*.md, *.txt, *.html) - in code and data a long dash can be the data itself
# (a fixture, a separator, a regex), and rewriting it silently would be worse
# than not checking at all.
#
# $DASH_GUARD_SKIP holds colon-separated glob patterns matched against the
# full file path; anything that matches passes through untouched. Use it for
# verbatim material you must not normalise (quotes, transcripts, imported
# documents):
#
#   export DASH_GUARD_SKIP='*/archive/*:*/quotes/*.md'
#
# Errors are fail open (exit 0, no output). Requires `jq` and `python3`.
# Tests: python3 tests/test_dash_guard.py
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE" ] && exit 0

HERE=$(cd "$(dirname "$0")" && pwd)

# Split on ':' with globbing off, so a pattern like */archive/* survives the
# split instead of expanding against the current directory. Unquoted $pat
# inside the case is what makes it match as a glob.
if [ -n "$DASH_GUARD_SKIP" ]; then
  OLD_IFS=$IFS
  set -f
  IFS=:
  for pat in $DASH_GUARD_SKIP; do
    case "$FILE" in
      $pat) exit 0 ;;
    esac
  done
  IFS=$OLD_IFS
  set +f
fi

case "$FILE" in
  *.md|*.txt|*.html)
    OUT=$(printf '%s' "$INPUT" | python3 "$HERE/dash-guard.py" "$FILE" 2>/dev/null)
    if [ -n "$OUT" ]; then
      printf '%s' "$OUT"
      exit 0
    fi
    ;;
esac
exit 0
