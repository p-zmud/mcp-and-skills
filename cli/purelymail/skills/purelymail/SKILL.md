---
name: purelymail
description: >-
  Drive a Purelymail mailbox through the `pmail` CLI - read, search, send and reply to mail over
  IMAP/SMTP, plus account administration through API v0 (domains, mailboxes, aliases/routing,
  app passwords, account credit). Use whenever the user talks about their Purelymail mail:
  "check my inbox", "any new mail", "unread messages", "send an email", "reply to that message",
  "find the email from X", "make an alias", "forward that address", "add a mailbox",
  "purelymail" - including when the word "Purelymail" is never said. Not for mailboxes at other
  providers (Gmail, Outlook), which have their own tooling. For mail tasks use `pmail`, never the
  Purelymail webmail.
---

# Purelymail (pmail)

One CLI for both Purelymail layers. Stdlib-only Python: no virtualenv, no pip.

```bash
pmail <command> [options]      # if it is not on PATH: ${CLAUDE_PLUGIN_ROOT}/bin/pmail
```

**Why two layers:** Purelymail's API v0 is account administration only - it cannot read, search
or send mail. Message content moves exclusively over IMAP/SMTP, authenticated with an app
password. `pmail` glues both layers into one tool, because `createAppPassword` from the API mints
that password itself - the user never pastes anything.

Output: UTF-8 JSON on stdout (exception: `read` prints readable text, `--json` gives the
structure). Errors: stderr + exit 2, never a silent skip.

## Setup

Once per machine:

```bash
pmail setup --token <API_TOKEN>          # token from the Purelymail panel -> Account -> API
pmail setup --default you@example.com    # change the default mailbox
```

`setup` calls `listUser`, generates an app password (`pmail-cli`) for every mailbox and stores
them in `~/.config/pmail/config.json` (directory 700, file 600). It is idempotent - a mailbox
that already has an entry is skipped. The token lives in that file only, never in a repo and
never in this skill.

Every mail command takes `--mailbox <address>` to reach a mailbox other than the default.

## Mail

```bash
pmail inbox                                  # 20 most recent, newest first
pmail inbox -n 5 --unread                    # unread only
pmail inbox --folder Sent                    # another folder
pmail folders                                # INBOX, Sent, Drafts, Trash, Junk, Archive

pmail search "invoice"                       # phrase anywhere in the message, accents included
pmail search --from john@example.com --since 2026-08-01
pmail search "order" --folder Archive -n 50

pmail read 42                                # headers + body, readable
pmail read 42 --json                         # the same as a structure
pmail read 42 --folder Sent

pmail send --to someone@example.com --subject "Subject" --body "Text"
pmail send --to a@x.com b@y.com --cc c@z.com --subject S --body-file /path/body.md \
           --attach report.pdf
pmail reply 42 --body "Answer"               # correct In-Reply-To/References
pmail reply 42 --body "..." --all            # reply-all

pmail mark 42 read | unread
pmail mark 42 delete --yes                   # -> Trash; inside Trash it deletes for good
```

UIDs from `inbox`/`search` go straight into `read`/`reply`/`mark` - they are stable within a
folder. Browsing does not mark mail as read (the folder is opened readonly).

## Administration

```bash
pmail credit                                 # account balance
pmail users
pmail user get you@example.com
pmail user create new@example.com --password 'xxx' [--recovery-email a@b.com]
pmail user modify you@example.com --new-password 'xxx' --two-factor yes
pmail user rm old@example.com --yes

pmail domains [--shared]
pmail domain add new.example | rm new.example --yes | settings example.com --recheck-dns
pmail domain ownership-code

pmail alias list [--domain example.com]      # aliases are routing rules
pmail alias add --domain example.com --match shop --target you@example.com
pmail alias add --domain example.com --match newsletter --target you@example.com --prefix
pmail alias rm --id 123852 --yes             # id comes from `alias list`

pmail apppass create you@example.com --name mobile-client [--save]
pmail apppass rm you@example.com --password <full-password> --yes
```

`--yes` is required for `user rm`, `domain rm`, `alias rm`, `apppass rm` and `mark ... delete`.
`domain rm` prints how many mailboxes would disappear with the domain before it asks.

## Gotchas

- **There is no mail API.** Reading and sending are IMAP/SMTP - if a mailbox has no app password
  in the config, mail commands fail and `pmail setup` has to be run.
- **An alias is a routing rule**, not a separate object. `--match shop` catches `shop@domain`,
  `--prefix` also catches `shop*@domain`, `--catchall` catches everything that is not an existing
  mailbox.
- **`user rm` deletes the mail together with the mailbox** - irreversibly. An alias/routing rule
  is enough when the goal is only to forward an address.
- **An API error can arrive with HTTP 200** (`{"type":"error",...}`) - `pmail` catches that, but
  hand-written `curl` calls to Purelymail have to check the `type` field, not the status code.
- **Non-ASCII phrases in `search` work**, but only in the phrase itself (`TEXT`); `--from` must be
  ASCII - details in `references/imap.md`.
- **Sent mail lands in `Sent` through an APPEND** done by `pmail` - Purelymail does not do it, so
  a message sent by another tool disappears without a trace.
- App passwords cannot be listed through the API. `apppass rm` needs the full password; unknown
  ones have to be removed in the Purelymail panel.

## Read on demand

- `references/api.md` - all 19 API v0 operations, request/response schemas, field-name traps
  (`userName` means the local part in one call and the full address in another).
- `references/imap.md` - folders, capabilities, exact SEARCH syntax, the UTF-8 variants that were
  tried, deletion behaviour.

Tests: `pytest tests/` from the plugin root (mocked, offline, sends nothing).
