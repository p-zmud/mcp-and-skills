# Purelymail API v0 - endpoint map

Source: Purelymail's `openapi.json`, verified against a live account 2026-08-05.

- Base: `https://purelymail.com/api/v0/<operation>`
- **Always POST**, even for reads. The body is always JSON (an empty object `{}` when there are
  no parameters).
- Auth: header `Purelymail-Api-Token: <token>` (not Bearer, not Authorization).
- Success response: `{"type":"success","result":{...}}`
- Error response: `{"type":"error","code":"invalidToken","message":"Token not valid."}` -
  **it can arrive with HTTP 200**, so checking the status code is not enough. `api_call()`
  in `pmail` looks at `type`.

## What is NOT here

No endpoints for reading, searching or sending mail. Message content is reachable only over
IMAP/SMTP - see `imap.md`. API v0 is pure account administration.

## The 19 operations

| Operation | Request | Result | In `pmail` |
|---|---|---|---|
| `checkAccountCredit` | `{}` | `{credit: string}` | `credit` |
| `listDomains` | `{includeShared?: bool}` | `{domains: [ApiDomainInfo]}` | `domains [--shared]` |
| `addDomain` | `{domainName}` | `{}` | `domain add` |
| `deleteDomain` | `{name}` | `{}` | `domain rm --yes` |
| `updateDomainSettings` | `{name, allowAccountReset?, symbolicSubaddressing?, recheckDns?}` | `{}` | `domain settings` |
| `getOwnershipCode` | `{}` | `{code: string}` | `domain ownership-code` |
| `listUser` | `{}` | `{users: [string]}` | `users` |
| `getUser` | `{userName}` | `GetUserResponse` | `user get` |
| `createUser` | `{userName, domainName, password, enablePasswordReset?, recoveryEmail?, recoveryEmailDescription?, recoveryPhone?, recoveryPhoneDescription?, enableSearchIndexing?, sendWelcomeEmail?}` | `{}` | `user create` |
| `modifyUser` | `{userName, newUserName?, newPassword?, enableSearchIndexing?, enablePasswordReset?, requireTwoFactorAuthentication?}` | `{}` | `user modify` |
| `deleteUser` | `{userName}` | `{}` | `user rm --yes` |
| `listRoutingRules` | `{}` | `{rules: [RoutingRule]}` | `alias list` |
| `createRoutingRule` | `{domainName, prefix, matchUser, targetAddresses[], catchall?}` | `{}` | `alias add` |
| `deleteRoutingRule` | `{routingRuleId: number}` | `{}` | `alias rm --yes` |
| `createAppPassword` | `{userHandle, name?}` | `{appPassword: string}` | `apppass create`, `setup` |
| `deleteAppPassword` | `{userName, appPassword}` | `{}` | `apppass rm --yes` |
| `listPasswordReset` | `{userName}` | `{users: [...]}` | unused |
| `upsertPasswordReset` | `{userName, type: "email"\|"phone", target, existingTarget?, description?, allowMfaReset?}` | `{}` | unused |
| `deletePasswordReset` | `{userName, target?}` | `{}` | unused |

The three `*PasswordReset` operations have no CLI equivalent (recovery methods are set once, in
the web panel). If they are ever needed, the schemas are above - add them to `pmail` through
`api_call()`.

## Response shapes

```jsonc
// ApiDomainInfo
{"name":"example.com","allowAccountReset":true,"symbolicSubaddressing":true,"isShared":false,
 "dnsSummary":{"passesMx":true,"passesSpf":true,"passesDkim":true,"passesDmarc":true}}

// RoutingRule  (the id is what `alias rm --id` needs)
{"id":123852,"domainName":"example.com","prefix":false,"matchUser":"shop",
 "targetAddresses":["you@example.com"],"catchall":false}

// GetUserResponse
{"enableSearchIndexing":bool,"recoveryEnabled":bool,"requireTwoFactorAuthentication":bool,
 "enableSpamFiltering":bool,"resetMethods":[...]}
```

## Gotchas

- **`userName` means two different things.** In `createUser` it is the local part alone (`you`),
  with `domainName` passed separately. Everywhere else (`getUser`, `modifyUser`, `deleteUser`,
  `deleteAppPassword`) it is the full address `you@example.com`. In `createAppPassword` the field
  is called `userHandle` and is a full address too.
- **`deleteDomain` uses the field `name`**, not `domainName` the way `addDomain` does. It deletes
  every user on the domain, which is why `pmail domain rm` first prints how many are affected.
- **Aliases are routing rules.** Purelymail has no separate "alias" object; an alias is a
  `matchUser` -> `targetAddresses` rule. `prefix: true` also matches `match*`, `catchall: true`
  catches everything that did not land in an existing user.
- **`createAppPassword` works without 2FA** (checked live). It returns a 20-character password -
  the only place it is ever shown, because the API has no way to list app passwords.
  `deleteAppPassword` needs the full password, so one that was never stored cannot be removed
  through the API later (only through the web panel).
- `credit` comes back as a string with roughly 70 decimal places - not a bug, that precision is on
  Purelymail's side.
- The "Refresh API Key" button in the panel invalidates the token; the old one stops working
  immediately and `pmail setup --token <new>` has to be repeated.
