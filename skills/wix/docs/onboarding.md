# Onboarding

Get the skill connected first, then ask your agent to do the first safe check.

If setup goes well, the next step is simple: ask your agent to check the connection, explain what it can review safely, and stop before any live change.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill the required fields for the real tool.

## Step 2: Get the right API access

Create a Wix app credential set in the Wix developer console and install the app where you want to run commands.

In `.env`, set:

- `WIX_APP_ID` (your Wix app ID)
- `WIX_APP_SECRET` (your Wix app secret)
- `WIX_INSTANCE_ID` (the app instance ID)

For this tool’s account-level Sites and Domains commands, you also need account-level auth values:

- `WIX_API_KEY` (the Wix account API key)
- `WIX_ACCOUNT_ID` (the Wix account ID that owns the sites)

Then run:

```bash
wix-safe-agent-cli auth token create
```

If you need to run Sites queries without setting app credentials, use the account-level values above. Sites requests use:

- `Authorization: <API_KEY>`
- `wix-account-id: <ACCOUNT_ID>`

Those headers are what the tool sends for:
- `wix-safe-agent-cli sites query`
- `wix-safe-agent-cli sites count`
- `wix-safe-agent-cli domain-dns get-zone`
- `wix-safe-agent-cli domain-dns preview-zone`
- `wix-safe-agent-cli site-actions bulk-delete`
- `wix-safe-agent-cli site-actions duplicate`
- `wix-safe-agent-cli site-actions publish`
- `wix-safe-agent-cli projects create-project`

Officially for API keys, Wix uses either `wix-account-id` or `wix-site-id` and does not support sending both.
- `wix-safe-agent-cli site-actions publish` uses `wix-site-id` in `POST /site-publisher/v1/site/publish`.
- `wix-safe-agent-cli projects create-project` uses `POST /funnel/projects/v1/create` and supports optional `--template-id`, `--folder-id`, and `--apps-json` fields with a required local `--name`.
- `wix-safe-agent-cli projects create-project` only supports `--type WIX` in this boundary, and the official account-level Projects API currently documents `create-project` only.
- Project read/list/query is not documented in that subtree; use account-level Sites commands (`sites query`, `sites count`) to retrieve existing sites.
- `wix-safe-agent-cli domain-dns get-zone` and `wix-safe-agent-cli domain-dns preview-zone` are the safe read-only Domain DNS commands in this boundary. Real DNS write methods stay excluded because Wix documents nameserver-only update behavior for external domains and a 50-values-per-record-type limit.
- `wix-safe-agent-cli branches get-default`, `wix-safe-agent-cli branches get`, and `wix-safe-agent-cli branches query` use the app-token path and need `Manage Site Branches`. The API manages branch metadata only; branch content editing still happens in the editor.

## Auth family matrix

| Command family | Required auth in this tool | Boundary note |
|---|---|---|
| `onboarding`, `auth token *`, `runs *` | no live Wix auth for local helper commands | local helper path only |
| `auth check` | whichever auth values you actually configured | checks the configured path, read-only |
| `contacts`, `members`, `app-installations`, `branches`, `files`, `data-items`, `data-collections` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` or valid `WIX_ACCESS_TOKEN` | app/site context required |
| `contributors query`, `contributors remove`, `contributors change-role`, `contributors change-contributor-location` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` or valid `WIX_ACCESS_TOKEN` | site contributor boundary only; live-unverified; `Manage Contributors` for the main contributor methods |
| `sites`, `domains`, `domain-dns`, `connected-domains`, `site-actions`, `site-folders`, `projects create-project` | `WIX_API_KEY` plus `WIX_ACCOUNT_ID` | account-level boundary; some families stay beta-gated or live-unverified |
| `ai-credits get-balance` | `WIX_API_KEY` only | Developer Preview; live-unverified; no `wix-account-id` header |
| `accounts get`, `accounts list-child-accounts` | `WIX_API_KEY` plus `WIX_ACCOUNT_ID` | signed-contract gate in official Wix docs; live-unverified |

If you need to use a manually issued token, place it in `WIX_ACCESS_TOKEN` or store it with:

```bash
wix-safe-agent-cli auth token set --file token.json
```

Good onboarding copy should:
- use short numbered steps
- say exactly what to copy and where it goes
- name the exact key or token type required
- never ask the user to paste secrets into chat

## Step 3: What to ask your AI agent (examples)

These are normal requests, not commands.

- “Check that the skill is connected and tell me what it can review safely.”
- “Show me the first useful thing to look at in this account.”
- “Find likely issues or opportunities, then stop and explain them before any changes.”
- “Prepare a careful plan for these updates and wait for my approval.”

## What success looks like

Setup is working when the agent can:
- confirm the account or workspace is reachable
- explain what it can review right now
- show a safe next step without changing anything yet

If you want the command version of this setup, use [Run your first checks](quickstart.md).

## If something fails

The most common issues are:
- missing or incorrect values in `.env`
- the wrong key or token type
- account permissions that do not allow the requested action

The real tool should explain common errors in [the troubleshooting guide](troubleshooting.md).
