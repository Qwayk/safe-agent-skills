# Connect Xero

The normal local setup uses Xero’s OAuth 2.0 Authorization Code flow with PKCE. It needs a client ID, not a client secret. The tool asks only for the scopes needed by the fixed commands you choose and adds `offline_access` for refresh tokens.

Never paste a token, client secret, authorization code, or PKCE verifier into chat.

## 1. Create the Xero app

1. Open the [Xero developer portal](https://developer.xero.com/app/manage).
2. Create an OAuth 2.0 app with the “Auth Code with PKCE” grant type.
3. Add the exact redirect URI `http://localhost:8765/callback`, or choose another localhost URI and use the same value in `.env`.
4. Copy only the client ID into your local `.env` file.

## 2. Prepare the local settings

Installing the `xero` skill does not install the Python CLI. From the bundled or cloned `qwayk-xero-safe-agent-cli` folder, use Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-xero-safe-agent-cli --version
.venv/bin/qwayk-xero-safe-agent-cli onboarding
```

Open the created `.env` and set:

```dotenv
XERO_CLIENT_ID=your_local_client_id
XERO_REDIRECT_URI=http://localhost:8765/callback
```

The file is created with owner-only permissions. `.env` and `.state/` are excluded from Git.

## 3. Start authorization with minimum scopes

Name the fixed commands you plan to use:

```bash
qwayk-xero-safe-agent-cli auth start \
  --command accounting.get-organisations \
  --command accounting.get-invoices
```

Open the returned `authorization_url` in a browser. After Xero redirects to your localhost URI, copy the returned `code` into the ignored private path `.state/oauth/code.txt`. Use the returned `state` query value exactly:

```bash
qwayk-xero-safe-agent-cli auth exchange \
  --code-file .state/oauth/code.txt \
  --state returned_state_value
```

The tool checks the saved PKCE state, rejects requests older than 15 minutes, exchanges the code, and stores the token under `.state/oauth/` with owner-only permissions. Remove `.state/oauth/code.txt` after a successful exchange; the one-time code is no longer needed.

## 4. Discover and select the exact organisation

```bash
qwayk-xero-safe-agent-cli tenant list
qwayk-xero-safe-agent-cli tenant select --tenant-id exact_tenant_id --region AU
qwayk-xero-safe-agent-cli tenant show
```

Use `NZ`, `UK`, `US`, or `GLOBAL` when that is the real organisation region. Selection rechecks the live connections list and refuses a tenant ID that was not discovered or is not an organisation tenant.

## 5. Run one safe read

```bash
qwayk-xero-safe-agent-cli accounting.get-organisations
```

For sensitive results, save the full response to a protected file:

```bash
qwayk-xero-safe-agent-cli \
  --protected-output .state/protected/invoices.json \
  accounting.get-invoices \
  --input examples/get-invoices.json
```

## Optional: paid Custom Connection

A Custom Connection is paid and can connect to only one AU, NZ, UK, or US organisation. Put its separate client ID and client secret in `XERO_CUSTOM_CLIENT_ID` and `XERO_CUSTOM_CLIENT_SECRET`, then run:

```bash
qwayk-xero-safe-agent-cli auth client-credentials \
  --profile custom \
  --scope accounting.settings.read
qwayk-xero-safe-agent-cli tenant custom-discover
qwayk-xero-safe-agent-cli --auth-profile custom accounting.get-organisations
```

The organisation is discovered from Xero and stored separately. Custom Connection calls do not send `xero-tenant-id`.

## Optional: Xero App Store API

App Store commands use separate non-tenanted client credentials. Put them in the `XERO_APP_STORE_*` fields, request the exact documented scope with `auth client-credentials --profile app-store`, and then use the fixed `app-store.*` command. They never reuse an organisation token.

Only configure this profile for a legacy XASS transition. Xero deprecated Xero App Store Subscriptions in March 2026, accepted no new apps after 4 December 2025, and required existing customers to migrate by 1 July 2026. The four endpoints remain in the pinned and current API reference, but the tool cannot prove that your app is still entitled to use them or that a live call will succeed.

The fixed `identity.get-connections` command also uses non-tenanted client credentials with the `app.connections` scope. It requires an exact documented `Xero-Tenant-Id` or `Xero-User-Id` target header and does not use the selected organisation token.
