# Purelymail over IMAP/SMTP - folders, SEARCH, gotchas

Everything here was checked against a live account on 2026-08-05.

## Servers

| | host | port | encryption | login |
|---|---|---|---|---|
| IMAP | `imap.purelymail.com` | 993 | SSL/TLS | full address + app password |
| SMTP | `smtp.purelymail.com` | 465 | SSL/TLS (implicit) | same |

The app password is minted by `createAppPassword` in the API - `pmail setup` does that for every
mailbox on its own and stores the result in `~/.config/pmail/config.json`. The Purelymail web
panel password never has to be pasted anywhere.

## Folders

Dovecot, separator `.` (not `/`). A fresh account has exactly:

```
INBOX   Sent   Drafts   Trash   Junk   Archive
```

`pmail folders` reads them live - a folder created in webmail shows up immediately. Folder names
are quoted in commands, so spaces in a name are not a problem.

Server capabilities: `IMAP4REV1 LITERAL+ CHILDREN I18NLEVEL=1 NAMESPACE IDLE ENABLE CONDSTORE
QRESYNC ANNOTATION AUTH=PLAIN SASL-IR RIGHTS= WITHIN ESEARCH ESORT SEARCHRES SORT MOVE UIDPLUS
UNSELECT COMPRESS=DEFLATE`. The ones that matter: `MOVE` (used when deleting) and `UIDPLUS`.

## SEARCH

`pmail` always searches by UID (`UID SEARCH`), so the numbers from `inbox`/`search` are stable
within a folder and can be handed straight to `read`/`reply`/`mark`.

Criteria the CLI assembles:

```
pmail search "invoice"                       -> TEXT "invoice"
pmail search --from john@example.com         -> FROM "john@example.com"
pmail search --since 2026-08-01              -> SINCE 01-Aug-2026
pmail search "x" --from a@b.com --since ...  -> all of them at once (AND)
```

IMAP dates must be `DD-Mon-YYYY` with English month names - `pmail` converts from `YYYY-MM-DD`
by itself.

### Non-ASCII phrases - solved

Variants that were tried:

| variant | outcome |
|---|---|
| `M.uid("SEARCH", None, "TEXT", "café")` | `UnicodeEncodeError` (imaplib encodes as ASCII) |
| `M.search("UTF-8", "TEXT", b"...")` | `BAD SEARCH failed. Illegal arguments.` |
| `M.uid("SEARCH", "CHARSET", "UTF-8", "TEXT", b"...")` | `BAD UID failed. Illegal arguments.` |
| **`M.literal = phrase.encode("utf-8")` + `M.uid("SEARCH","CHARSET","UTF-8","TEXT")`** | **OK** |

So: Dovecot accepts `CHARSET UTF-8` only when the phrase itself travels as an **IMAP literal**.
`uid_search()` in `pmail` switches to that path automatically as soon as the phrase is not ASCII.
Client-side filtering turned out to be unnecessary.

Limitation: imaplib sends only one literal per command, so the literal is reserved for the `TEXT`
phrase (always last). `--from` with non-ASCII characters fails loudly instead of being dropped
silently - and addresses are ASCII anyway.

## Sending

- `pmail send` does SMTP and **then an IMAP APPEND into `Sent` with the `\Seen` flag**. Purelymail
  does not record sent mail by itself - without the APPEND the message vanishes without a trace.
- `Message-ID` is generated locally (`email.utils.make_msgid` with the mailbox domain) so that
  `reply` has something to put in `In-Reply-To`.
- `reply` takes `Reply-To`, falling back to the original `From`; `References` = the original
  `References` plus its `Message-ID`. `--all` adds the original `To`/`Cc` addresses to Cc, minus
  your own address.
- Bodies are always UTF-8 (`EmailMessage.set_content`); attachment MIME types are guessed from the
  file extension.

## Deleting

`pmail mark <uid> delete --yes`:
- in a normal folder - `UID MOVE` to `Trash` (reversible, the way every client behaves),
- inside `Trash` itself - `+FLAGS (\Deleted)` + `EXPUNGE`, that is, gone for good.

The `--yes` guard is mandatory in both cases.

## Reading content

- `text/plain` is preferred; for HTML-only mail the tags go through a small `HTMLParser`
  (`script`/`style` dropped, `p`/`br`/`div`/`tr`/`li` produce a newline).
- Headers (`Subject`, `From`) go through `decode_header` + `make_header`, so `=?UTF-8?B?...?=`
  comes back as ordinary text with its accents intact.
- Attachments are **listed by name only** - `pmail read` does not write them to disk.
- `read` and `inbox`/`search` open the folder `readonly`, so browsing **does not mark messages as
  read**. That is what `pmail mark <uid> read` is for.
