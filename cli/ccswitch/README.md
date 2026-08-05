# ccswitch

Switch Claude Code accounts through `CLAUDE_CODE_OAUTH_TOKEN`. One account is one token, the
active account is the token exported from `~/.zshenv`, and nothing goes through the Keychain -
so it works headless, over SSH and inside tmux.

**Portfolio entry.** This one is not in `marketplace.json` and there is no `/plugin install` for
it: it is a single bash script to read and copy, not something to install blind. It rewrites
`~/.zshenv`, edits `~/.claude/.credentials.json` and can install a launchd agent, and you should
read the section below before you let any script do that.

**macOS only.** It stands on BSD `stat`, `security`, `launchctl` and `lsof`.

## The problem it solves

Claude Code has two ways to know who you are, and they do not agree.

`CLAUDE_CODE_OAUTH_TOKEN` in the environment is the headless path: no browser, no Keychain, and
switching accounts is one variable away. `/login` is the interactive path: it writes
`~/.claude/.credentials.json` (the `claudeAiOauth` key) plus a Keychain entry
`Claude Code-credentials`.

**The `/login` credentials win.** Set the env token, start a session, and if that file has
`claudeAiOauth` in it you are still on the `/login` account. Worse, deleting the file does not
end it: a long-running `claude` session holds the refresh token in memory and rewrites the file
roughly every 8 hours, so the problem comes back hours later with no visible cause. And
`/status` inside Claude reports the `/login` account, so the one thing you would check to
diagnose this actively lies to you.

ccswitch is the answer to that: switch the token, remove what overrides it, and keep it removed.

## Commands

```bash
ccswitch add <name> [--no-verify]     # paste a token (Enter imports the currently active one)
ccswitch list [--fast]                # accounts + a live OK/LIMIT/FAILED check per account
ccswitch use <name> [--keep-login]    # make it the account for NEW sessions
ccswitch current                      # which account is active, and does its token still work
ccswitch doctor [--fix]               # eight checks on whether switching will actually hold
ccswitch guard on|off|status          # launchd watcher that strips returning /login credentials
ccswitch remove <name>
ccswitch fingerprint [--if-stale <s>] # refresh the per-account rate-limit fingerprints
```

A new account starts with `claude setup-token` (log into the right account in the browser), then
`ccswitch add <name>` with the token it prints.

`ccswitch use <name>` affects **new** sessions only. Running sessions keep the account they
started on until they restart.

## What it modifies

Four things, and nothing else:

| Target | What happens |
| ------ | ------------ |
| `~/.zshenv` | One line, `export CLAUDE_CODE_OAUTH_TOKEN='...'`. The old file is copied to `~/.config/ccswitch/zshenv.bak` first, the new one is built in a temp file on the same filesystem and moved into place, so the write is atomic. Only that one line is ever touched, and the file ends up `600`. |
| `~/.claude/.credentials.json` | **Only the `claudeAiOauth` key is deleted.** `mcpOAuth` - the OAuth logins of your MCP servers - stays. The whole file is copied to `~/.config/ccswitch/creds-backups/` before every change (last 10 kept), and the rewrite is atomic. If the file cannot be parsed, it is left alone and you get told. |
| Keychain entry `Claude Code-credentials` | Deleted by `use` and `doctor --fix`, because it overrides the env token the same way the file does. If macOS refuses, you get a message pointing at Keychain Access rather than a silent failure. |
| `~/Library/LaunchAgents/com.ccswitch.guard.plist` | Only when you run `ccswitch guard on`. A `WatchPaths` agent on the credentials file that runs `ccswitch guard-run` whenever it changes. `ccswitch guard off` unloads it and renames the plist to `.disabled`. |

Tokens live in `~/.config/ccswitch/<name>.token`, mode `600`, directory `700`. They are secrets
in plaintext - exactly the same exposure as the `.zshenv` line they end up in. Nothing here
prints a whole token: every display is masked to the first 13 and last 6 characters.

`$CCSWITCH_HOME`, `$CCSWITCH_ZSHENV` and `$CCSWITCH_CLAUDE_DIR` redirect all three locations,
which is how you try this out without touching anything real:

```bash
TMP=$(mktemp -d)
CCSWITCH_HOME=$TMP CCSWITCH_ZSHENV=$TMP/zshenv CCSWITCH_CLAUDE_DIR=$TMP/claude \
  CCSWITCH_SKIP_PROBE=1 CCSWITCH_SKIP_KEYCHAIN=1 ./bin/ccswitch list
```

## Why surgical removal matters

`~/.claude/.credentials.json` is not only the `/login` account. It also holds `mcpOAuth`, the
OAuth state of every MCP server you have authorised. Delete the file to fix your account and you
silently log out of all of them, which surfaces later as unrelated 401s from servers that worked
yesterday.

So the removal is one key: load the JSON, `del data["claudeAiOauth"]`, write it back. Everything
else survives, and a full copy of the original goes to `creds-backups/` first, so undoing a
mistaken strip is pasting one key back.

## The guard

`ccswitch guard on` installs a launchd agent watching the credentials file. Every time the file
changes, `ccswitch guard-run` strips `claudeAiOauth` again, logs what it did to
`~/.config/ccswitch/guard.log`, and optionally notifies you.

It is a workaround, not a cure. The cure is restarting the long-running `claude` session that
keeps rewriting the file, and `ccswitch doctor` lists those sessions with their pid, uptime and
working directory so you know which terminal to go to. The guard is what keeps your accounts
straight in the meantime.

**Notifications** go through `$CCSWITCH_NOTIFY_CMD`, which runs under `sh -c` with the message as
`$1`. Unset means silence.

```bash
export CCSWITCH_NOTIFY_CMD='terminal-notifier -title ccswitch -message "$1"'
export CCSWITCH_NOTIFY_CMD='curl -s -X POST https://example.com/hook --data-urlencode "text=$1"'
```

## OK, LIMIT, FAILED

Every account check is a real request to `api.anthropic.com` with a 1-token completion, so it
tells you something a config file cannot:

- **OK** - the account works.
- **LIMIT** - the token is fine, the account is out of quota right now, and the label carries the
  reset time. Switching worked; that account just cannot do anything until it resets. Quota is
  per account, so claude.ai in a browser and your other machines burn the same pool.
- **FAILED** - the token does not authenticate. Mint a new one with `claude setup-token`.

The token goes to `curl` through stdin (`-H @-`), never as an argument, so it never appears in
`ps` output.

The reset timestamps returned by those calls are also an account fingerprint: two accounts
almost never share a 5-hour and 7-day reset pair. `ccswitch fingerprint` caches them in
`~/.config/ccswitch/fingerprints.json`, which is enough for a status line to tell you which
account a running session is actually billing.

## doctor

```console
$ ccswitch doctor
ccswitch doctor - is account switching actually going to hold?

✓ Credentials file has no claudeAiOauth (mcpOAuth may stay - that is MCP server OAuth).
✓ Keychain has no "Claude Code-credentials" entry.
✓ The active token in zshenv is account "work" (sk-ant-oat01-…Ab3xQ7).
Checking the active token… OK
✓ launchd guard is active (com.ccswitch.guard).
✓ fingerprints.json is fresh (4 min).

Verdict: HEALTHY - new sessions will use the ccswitch account.
```

Eight checks: the credentials file, the Keychain entry, the token in `~/.zshenv` and its prefix,
permissions on the store, the tokens and `~/.zshenv`, a live probe of the active token,
long-running `claude` sessions, the guard, and fingerprint freshness. `--fix` repairs everything
repairable and re-checks it afterwards, rather than assuming the fix worked.

## Install

```bash
git clone https://github.com/p-zmud/mcp-and-skills.git
ln -s "$PWD/mcp-and-skills/cli/ccswitch/bin/ccswitch" ~/.local/bin/ccswitch
ccswitch help
```

The guard plist points at the path the script was invoked from, so a symlinked install works
without editing anything.

## License

MIT - see the [repository root](https://github.com/p-zmud/mcp-and-skills).
