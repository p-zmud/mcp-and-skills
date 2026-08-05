#!/usr/bin/env python3
"""Tests for big-read-guard (hooks/big-read-guard.sh, PreToolUse Read).

Contract: the hook reads a JSON payload on stdin; when the Read targets a TEXT
file larger than the threshold and carries no explicit offset or limit, stdout
is JSON with hookSpecificOutput.permissionDecision == "deny" and exit 0. In
every other case (small file, image, PDF, explicit offset or limit, missing
file, missing file_path, garbage stdin) there is no decision and exit 0
(fail open).

Run: python3 tests/test_big_read_guard.py
Run it after every edit to big-read-guard.sh.
"""
import json
import os
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "hooks", "big-read-guard.sh")
TMPDIR = tempfile.mkdtemp(prefix="bigread-fixtures-")

results = []


def run_hook(stdin_text, env=None):
    return subprocess.run(
        ["bash", HOOK], input=stdin_text, capture_output=True,
        text=True, timeout=10, env=env,
    )


def decision_of(p):
    if not p.stdout.strip():
        return None
    try:
        out = json.loads(p.stdout)
    except ValueError:
        return "UNPARSABLE-STDOUT"
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision")


def payload(path, **extra):
    ti = {"file_path": path}
    ti.update(extra)
    return json.dumps({"session_id": "t", "tool_name": "Read", "tool_input": ti})


def make(name, size):
    path = os.path.join(TMPDIR, name)
    with open(path, "wb") as f:
        f.write(b"x" * size)
    return path


def check(name, stdin_text, expect_deny, env=None):
    try:
        p = run_hook(stdin_text, env=env)
    except subprocess.TimeoutExpired:
        results.append((name, False, "TIMEOUT"))
        return
    dec = decision_of(p)
    ok = (dec == "deny") if expect_deny else (dec is None)
    detail = f"exit={p.returncode} decision={dec}"
    if p.returncode != 0:
        ok = False
        detail += " (exit != 0)"
    results.append((name, ok, detail))


BIG = 40000
SMALL = 1000

check("small text file -> allow", payload(make("small.py", SMALL)), False)
check("big .py -> deny", payload(make("big.py", BIG)), True)
check("big .html -> deny", payload(make("big.html", BIG)), True)
check("big file with no extension -> deny", payload(make("bigfile", BIG)), True)
check("big .jpg -> allow (images are cheap once the API rescales them)",
      payload(make("big.jpg", BIG)), False)
check("big .PNG uppercase -> allow", payload(make("big.PNG", BIG)), False)
check("big .pdf -> allow (it has a pages parameter)", payload(make("big.pdf", BIG)), False)
check("big file with limit -> allow (deliberate read)",
      payload(make("big2.py", BIG), limit=2000), False)
check("big file with offset -> allow", payload(make("big3.py", BIG), offset=100), False)
check("exactly the 32768 threshold -> allow", payload(make("edge.py", 32768)), False)
check("threshold + 1 -> deny", payload(make("edge2.py", 32769)), True)
check("missing file -> allow (fail open)",
      payload(os.path.join(TMPDIR, "nosuch.py")), False)
check("no file_path -> allow",
      json.dumps({"session_id": "t", "tool_name": "Read", "tool_input": {}}), False)
check("garbage stdin -> allow (fail open)", "this is not json", False)
check("directory -> allow", payload(TMPDIR), False)

# BIG_READ_GUARD_THRESHOLD raises and lowers the limit; garbage falls back to 32768
env_high = dict(os.environ, BIG_READ_GUARD_THRESHOLD="65536")
check("threshold raised by env -> allow", payload(make("env1.py", BIG)), False, env=env_high)
env_low = dict(os.environ, BIG_READ_GUARD_THRESHOLD="500")
check("threshold lowered by env -> deny", payload(make("env2.py", SMALL)), True, env=env_low)
env_junk = dict(os.environ, BIG_READ_GUARD_THRESHOLD="lots")
check("garbage threshold -> falls back to 32768", payload(make("env3.py", BIG)), True,
      env=env_junk)

deny_p = run_hook(payload(make("msg.py", BIG)))
try:
    reason = json.loads(deny_p.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    ok = "Grep" in reason and "offset/limit" in reason and "KB" in reason
except Exception:
    ok = False
results.append(("deny message points at Grep + offset/limit", ok, ""))

fails = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {detail}")
print(f"\n{len(results) - len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
