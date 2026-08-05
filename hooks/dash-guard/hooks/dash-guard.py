#!/usr/bin/env python3
"""dash-guard: reduces long dashes to a hyphen in prose files.

Stdin: the PreToolUse (Write|Edit) payload as JSON. Argv[1]: file_path.
Stdout: the hook's JSON with hookSpecificOutput.updatedInput when the content
needs fixing; EMPTY output when there is nothing to fix. Errors produce empty
output (fail open) - a typography guard never breaks a write.

U+2014 (em dash) and U+2013 (en dash) are replaced with a hyphen, character
for character, leaving the surrounding spaces alone. In .md files the contents
of fenced blocks and inline code are skipped, otherwise the autofix would
mangle the examples in the documentation of this very rule. In .txt and .html
the whole content is rewritten.

Called from dash-guard.sh, which decides which files are in scope.
Tests: python3 tests/test_dash_guard.py
"""
import json
import re
import sys

EM = chr(8212)
EN = chr(8211)

# One capturing group: re.split returns the protected fragments at odd
# indexes. An orphaned fence (never closed) protects the text to the end of
# the file - hence the [\s\S]*$ variants at the end of the alternation.
PROTECTED = re.compile(
    r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`|```[\s\S]*$|~~~[\s\S]*$)'
)


def sub_plain(text):
    """Replace across the whole content. Returns (new_text, count)."""
    n = text.count(EM) + text.count(EN)
    if n:
        text = text.replace(EM, "-").replace(EN, "-")
    return text, n


def sub_markdown(text):
    """Replace outside fenced blocks and inline code."""
    parts = PROTECTED.split(text)
    total = 0
    for i in range(0, len(parts), 2):
        parts[i], n = sub_plain(parts[i])
        total += n
    return "".join(parts), total


def main():
    try:
        data = json.load(sys.stdin)
        ti = data.get("tool_input") or {}
        path = sys.argv[1] if len(sys.argv) > 1 else ti.get("file_path", "")
        key = "content" if isinstance(ti.get("content"), str) else "new_string"
        text = ti.get(key)
        if not isinstance(text, str) or (EM not in text and EN not in text):
            return
        fix = sub_markdown if path.endswith(".md") else sub_plain
        new_text, n = fix(text)
        if n == 0:
            return
        updated = dict(ti)
        updated[key] = new_text
        msg = "dash-guard: %d long dashes reduced to a hyphen" % n
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": updated,
                "additionalContext": msg + " - the version written to disk uses hyphens",
            },
            "systemMessage": msg,
        }))
    except Exception:
        pass


main()
