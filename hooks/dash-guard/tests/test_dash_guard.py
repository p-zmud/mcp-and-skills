#!/usr/bin/env python3
"""Tests for dash-guard: the transform (dash-guard.py) and the dispatcher (dash-guard.sh).

Contract of the transform: stdin = the PreToolUse payload as JSON, argv[1] =
file_path. Stdout = JSON with hookSpecificOutput.updatedInput when the content
needs fixing; EMPTY output when there is nothing to fix or when anything went
wrong (fail open). It never denies a write - there is no deny path at all.

Payloads are tested in BOTH JSON encodings: escaped (what json.dumps produces
by default) and raw UTF-8 (what Node's JSON.stringify sends in production).

Run: python3 tests/test_dash_guard.py
Run it after every edit to dash-guard.sh or dash-guard.py.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks")
SCRIPT = os.path.join(HOOKS_DIR, "dash-guard.py")
HOOK = os.path.join(HOOKS_DIR, "dash-guard.sh")
EM = chr(8212)
EN = chr(8211)
TMPDIR = tempfile.mkdtemp(prefix="dash-guard-fixtures-")

results = []


def payload(tool, path, content=None, old=None, new=None, raw=False):
    ti = {"file_path": path}
    if tool == "Write":
        ti["content"] = content
    else:
        ti["old_string"] = old
        ti["new_string"] = new
    return json.dumps({"session_id": "t", "tool_name": tool, "tool_input": ti},
                      ensure_ascii=not raw)


def newfile(rel):
    path = os.path.join(TMPDIR, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def run_script(stdin_text, path, timeout=10):
    t0 = time.time()
    p = subprocess.run(["python3", SCRIPT, path], input=stdin_text,
                       capture_output=True, text=True, timeout=timeout, cwd=TMPDIR)
    return p, time.time() - t0


def updated_of(p):
    """Returns updatedInput, or None when stdout is empty."""
    if not p.stdout.strip():
        return None
    out = json.loads(p.stdout)
    return (out.get("hookSpecificOutput") or {}).get("updatedInput")


def record(name, ok, detail=""):
    results.append((name, ok, detail))


def check_script(name, stdin_text, path, field=None, expect_text=None,
                 max_seconds=None):
    """field=None -> we expect EMPTY output (no change)."""
    try:
        p, dt = run_script(stdin_text, path)
    except subprocess.TimeoutExpired:
        record(name, False, "TIMEOUT")
        return
    try:
        upd = updated_of(p)
    except ValueError:
        record(name, False, "UNPARSABLE-STDOUT")
        return
    if field is None:
        ok = upd is None and p.returncode == 0
        record(name, ok, "stdout=%r rc=%d" % (p.stdout[:60], p.returncode))
        return
    if upd is None:
        record(name, False, "no updatedInput (stdout empty)")
        return
    got = upd.get(field)
    ok = got == expect_text and p.returncode == 0
    if ok and max_seconds is not None and dt > max_seconds:
        ok = False
    record(name, ok, "got=%r dt=%.2fs" % (got[:70] if got else got, dt))


# 1. Write .md: em dash and en dash both come down to a hyphen
check_script("md-write-both-characters",
             payload("Write", newfile("a.md"),
                     content="text %s aside, range 3%s5" % (EM, EN)),
             newfile("a.md"), field="content",
             expect_text="text - aside, range 3-5")

# 2/3. Edit .md: new_string is rewritten, old_string is left alone
edit_path = newfile("b.md")
p_edit = payload("Edit", edit_path, old="old %s text" % EM, new="new %s text" % EM)
check_script("md-edit-new-string", p_edit, edit_path, field="new_string",
             expect_text="new - text")
check_script("md-edit-old-string-untouched", p_edit, edit_path,
             field="old_string", expect_text="old %s text" % EM)

# 4. A fenced block in .md survives, the prose around it is fixed
fenced = "prose %s here\n\n```python\nSEP = \"%s\"\n```\n\nend %s here\n" % (EM, EM, EN)
check_script("md-code-block-skipped",
             payload("Write", newfile("c.md"), content=fenced),
             newfile("c.md"), field="content",
             expect_text="prose - here\n\n```python\nSEP = \"%s\"\n```\n\nend - here\n" % EM)

# 5. Inline code in .md survives
check_script("md-inline-code-skipped",
             payload("Write", newfile("d.md"),
                     content="prose %s here, code `x = \"%s\"` next to it" % (EM, EM)),
             newfile("d.md"), field="content",
             expect_text="prose - here, code `x = \"%s\"` next to it" % EM)

# 6. .txt: no code block logic, the whole content is rewritten
check_script("txt-whole-content",
             payload("Write", newfile("e.txt"), content="a %s b `c %s d`" % (EM, EM)),
             newfile("e.txt"), field="content", expect_text="a - b `c - d`")

# 7. .html: the whole content is rewritten
check_script("html-whole-content",
             payload("Write", newfile("f.html"), content="<p>a %s b</p>" % EM),
             newfile("f.html"), field="content", expect_text="<p>a - b</p>")

# 8. Content with no long dashes -> empty output (we do not rewrite for nothing)
check_script("no-dashes-no-output",
             payload("Write", newfile("g.md"), content="plain text - with a hyphen"),
             newfile("g.md"))

# 9. Raw UTF-8 encoding on stdin (the production payload)
check_script("raw-utf8",
             payload("Write", newfile("h.md"), content="text %s aside" % EM, raw=True),
             newfile("h.md"), field="content", expect_text="text - aside")

# 10. The ASCII escape sequence as source text is NOT a dash -> empty output
check_script("ascii-escape-is-not-a-dash",
             payload("Write", newfile("i.md"), content='{"sep": "\\\\u2014 as text"}'),
             newfile("i.md"))

# 11. Garbage input -> fail open (empty output, rc 0)
check_script("fail-open-garbage", "this is not json{{{", newfile("j.md"))

# 12. No content and no new_string -> empty output
check_script("no-content", payload("Write", newfile("k.md"), content=None),
             newfile("k.md"))

# 13. Large content (500 KB) -> fixed, and fast
big = ("lorem ipsum " * 40000) + EM
check_script("large-content", payload("Write", newfile("l.md"), content=big),
             newfile("l.md"), field="content",
             expect_text=("lorem ipsum " * 40000) + "-", max_seconds=5)

# 14. Response shape: hookEventName, additionalContext carrying the count,
#     NO permissionDecision, and no long dash anywhere in the decision channel
p_shape, _ = run_script(payload("Write", newfile("m.md"),
                                content="a %s b %s c" % (EM, EN)), newfile("m.md"))
try:
    out = json.loads(p_shape.stdout)
    hso = out.get("hookSpecificOutput") or {}
    ok = (hso.get("hookEventName") == "PreToolUse"
          and "permissionDecision" not in hso
          and "2" in (hso.get("additionalContext") or "")
          and bool(out.get("systemMessage"))
          and EM not in p_shape.stdout and EN not in p_shape.stdout)
    record("response-shape", ok, "hso=%r" % list(hso.keys()))
except ValueError:
    record("response-shape", False, "UNPARSABLE-STDOUT")


# --- integration: the dispatcher, dash-guard.sh -----------------------------

def run_hook(stdin_text, cwd=None, timeout=10, env=None):
    return subprocess.run(["bash", HOOK], input=stdin_text, capture_output=True,
                          text=True, timeout=timeout, cwd=cwd or TMPDIR, env=env)


def check_hook(name, stdin_text, field=None, expect_text=None, cwd=None, env=None):
    """field=None -> we expect no output at all from the hook."""
    try:
        p = run_hook(stdin_text, cwd=cwd, env=env)
    except subprocess.TimeoutExpired:
        record(name, False, "TIMEOUT")
        return
    if p.returncode != 0:
        record(name, False, "rc=%d" % p.returncode)
        return
    out = None
    if p.stdout.strip():
        try:
            out = json.loads(p.stdout)
        except ValueError:
            record(name, False, "UNPARSABLE-STDOUT: %r" % p.stdout[:80])
            return
    hso = (out or {}).get("hookSpecificOutput") or {}
    if "permissionDecision" in hso:
        record(name, False, "hook denied the write, it must never do that")
        return
    if field is None:
        record(name, out is None, "stdout=%r" % (p.stdout[:60],))
        return
    upd = hso.get("updatedInput") or {}
    record(name, upd.get(field) == expect_text, "got=%r" % (upd.get(field),))


# H1. .md through the whole hook -> autofix
check_hook("hook-md-autofix",
           payload("Write", newfile("h1.md"), content="text %s aside" % EM),
           field="content", expect_text="text - aside")

# H2. .txt and .html are in scope too
check_hook("hook-txt-autofix",
           payload("Write", newfile("h2.txt"), content="text %s aside" % EM),
           field="content", expect_text="text - aside")
check_hook("hook-html-autofix",
           payload("Write", newfile("h3.html"), content="<p>a %s b</p>" % EN),
           field="content", expect_text="<p>a - b</p>")

# H4. .py is out of scope -> no rewrite, no denial
check_hook("hook-py-out-of-scope",
           payload("Write", newfile("h4.py"), content="SEP = \"%s\"" % EM))

# H5. .sh is out of scope (the hook cannot rewrite itself)
check_hook("hook-sh-out-of-scope",
           payload("Edit", HOOK, old="x", new="EMDASH=\"%s\"" % EM))

# H6. DASH_GUARD_SKIP: a matching pattern passes the file through untouched
env_skip = dict(os.environ, DASH_GUARD_SKIP="*/archive/*:*/quotes/*.md")
check_hook("hook-skip-pattern-matches",
           payload("Write", newfile("archive/imported.md"), content="quote %s" % EM),
           env=env_skip)
check_hook("hook-skip-second-pattern-matches",
           payload("Write", newfile("quotes/interview.md"), content="quote %s" % EM),
           env=env_skip)

# H7. DASH_GUARD_SKIP set but not matching -> the autofix still runs
check_hook("hook-skip-pattern-does-not-match",
           payload("Write", newfile("notes/plan.md"), content="line %s one" % EM),
           field="content", expect_text="line - one", env=env_skip)

# H8. A skip pattern is never expanded against the current directory
os.makedirs(os.path.join(TMPDIR, "archive"), exist_ok=True)
open(os.path.join(TMPDIR, "archive", "decoy.md"), "w").close()
check_hook("hook-skip-pattern-not-glob-expanded-in-cwd",
           payload("Write", newfile("notes/second.md"), content="line %s two" % EM),
           field="content", expect_text="line - two", env=env_skip, cwd=TMPDIR)

# H9. A path with spaces (a real convention in note vaults)
check_hook("hook-path-with-spaces",
           payload("Write", newfile("2026 Q1/meeting notes.md"),
                   content="line %s one" % EM),
           field="content", expect_text="line - one")

# H10. Raw UTF-8 payload survives the bash layer
check_hook("hook-raw-utf8",
           payload("Write", newfile("h10.md"), content="text %s aside" % EM, raw=True),
           field="content", expect_text="text - aside")

# H11. Garbage input through the whole hook -> fail open
check_hook("hook-fail-open", "this is not json{{{")

# H12. No file_path -> fail open
check_hook("hook-no-file-path",
           json.dumps({"tool_name": "Write", "tool_input": {"content": "a %s b" % EM}}))

# --- summary ----------------------------------------------------------------
fails = [r for r in results if not r[1]]
for name, ok, detail in results:
    print("%s %-40s %s" % ("PASS" if ok else "FAIL", name, detail))
print("\n%d/%d PASS" % (len(results) - len(fails), len(results)))
sys.exit(1 if fails else 0)
