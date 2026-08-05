# purelymail

`pmail` - a single command line tool for both halves of [Purelymail](https://purelymail.com):
the mail itself (IMAP/SMTP) and the account behind it (API v0).

Stdlib-only Python 3. No virtualenv, no pip, no dependencies - one file you can drop on your
`PATH`. The plugin also ships a skill, so Claude Code knows when and how to drive it.

## Why the tool exists

Purelymail's API v0 does account administration and nothing else: domains, mailboxes, routing
rules, app passwords, credit. It **cannot read, search or send mail** - that only happens over
IMAP and SMTP, authenticated with an app password.

Every other approach means two tools and a manual step in the middle. `pmail` keeps them
together, because `createAppPassword` in the API mints the IMAP/SMTP password itself: you paste
an API token once, and `pmail setup` provisions every mailbox on the account.

## Install

As a Claude Code plugin:

```bash
# inside Claude Code
/plugin marketplace add p-zmud/mcp-and-skills
/plugin install purelymail@pzmud
```

As a plain CLI, put it on your `PATH`:

```bash
git clone https://github.com/p-zmud/mcp-and-skills.git
ln -s "$PWD/mcp-and-skills/cli/purelymail/bin/pmail" ~/.local/bin/pmail
pmail --help
```

## Configure

```bash
pmail setup --token <API_TOKEN>          # token from the Purelymail panel -> Account -> API
```

That calls `listUser`, generates an app password named `pmail-cli` for each mailbox and writes
everything to `~/.config/pmail/config.json` (directory `700`, file `600`). It is idempotent: a
mailbox that already has a password is skipped, never overwritten. `$PMAIL_CONFIG` overrides the
path.

```jsonc
{
  "api_token": "...",
  "default_mailbox": "you@example.com",
  "mailboxes": {"you@example.com": "app-password", "second@example.com": "app-password"}
}
```

**The token and the app passwords live in that file only.** Nothing here reads them from the
environment, prints them, or sends them anywhere except purelymail.com.

Switch the default mailbox later with `pmail setup --default <address>`; any single command can
override it with `--mailbox <address>`.

## Use

```bash
pmail inbox -n 5 --unread
pmail search "invoice" --since 2026-08-01
pmail read 42
pmail reply 42 --body "On it, thanks."
pmail send --to someone@example.com --subject "Report" --body-file report.md --attach report.pdf
pmail mark 42 delete --yes

pmail users
pmail alias add --domain example.com --match shop --target you@example.com
pmail apppass create you@example.com --name mobile-client
pmail credit
```

A full run, end to end:

```console
$ pmail inbox -n 2
{
  "mailbox": "you@example.com",
  "folder": "INBOX",
  "count": 2,
  "messages": [
    {
      "uid": 118,
      "from": "José Álvarez <jose@example.com>",
      "to": "you@example.com",
      "subject": "Überfällige Rechnung",
      "date": "Tue, 5 Aug 2026 09:00:00 +0200",
      "flags": ["\\Seen"],
      "unread": false
    }
  ]
}
```

Output is UTF-8 JSON on stdout, so it pipes into `jq` cleanly. The one exception is `read`, which
prints a readable message by default and JSON with `--json`.

## Behaviour worth knowing

- **Errors are loud.** Anything unexpected goes to stderr and exits `2`. There are no silent
  fallbacks and no partially-skipped records.
- **Destructive commands need `--yes`**: `user rm`, `domain rm`, `alias rm`, `apppass rm`, and
  `mark <uid> delete`. `domain rm` first prints how many mailboxes would die with the domain.
- **Browsing does not mark mail as read** - `inbox`, `search` and `read` open the folder
  `readonly`. Use `pmail mark <uid> read` when you mean it.
- **Sent mail is APPENDed to `Sent`** by the tool, because Purelymail does not record it server
  side. A message sent by anything that skips the APPEND leaves no trace in the mailbox.
- **An API error can arrive with HTTP 200** (`{"type":"error", ...}`), so the tool checks the
  `type` field rather than the status code.
- **Non-ASCII search works.** Dovecot only accepts `CHARSET UTF-8` when the phrase is sent as an
  IMAP literal; the tool switches to that path automatically. `--from` must stay ASCII and says
  so instead of quietly dropping the filter.

## Layout

```
bin/pmail                       the CLI, one stdlib-only file
skills/purelymail/SKILL.md      when and how Claude should reach for it
skills/purelymail/references/   API v0 endpoint map, IMAP/SMTP notes
tests/test_pmail.py             38 offline tests, urllib/imaplib/smtplib faked
```

## Tests

```bash
pytest tests/
```

38 tests, no network: `urllib.request.urlopen`, `imaplib.IMAP4_SSL` and `smtplib.SMTP_SSL` are all
replaced with fakes, and every test gets a throwaway config, so your real `~/.config/pmail` is
never touched and no mail is ever sent.

## License

MIT - see the [repository root](https://github.com/p-zmud/mcp-and-skills).

Provided as is, with no warranty and no support. Use it at your own risk - the author
accepts no responsibility for any damage, data loss or other consequence of running it.
