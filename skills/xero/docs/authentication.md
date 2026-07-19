# Authentication

The tool keeps three Xero auth paths separate so one credential cannot silently stand in for another.

## PKCE for normal local use

This is the default for tenanted Accounting, Assets, Bank Feeds, Files, Finance, Payroll, Projects, and eInvoicing commands.

- Uses Authorization Code with PKCE and no client secret.
- Requests `offline_access` and only the minimum data scopes for the fixed commands named in `auth start`. It does not request `openid` because this CLI does not use Xero identity claims.
- Uses current granular Accounting scopes where Xero documents them.
- Stores PKCE state and tokens under `.state/oauth/` with mode `0600`.
- Requires live tenant discovery and exact selection before tenanted commands.

Useful commands:

```bash
qwayk-xero-safe-agent-cli auth start --command accounting.get-invoices
qwayk-xero-safe-agent-cli auth exchange --code-file .state/oauth/code.txt --state returned_state
qwayk-xero-safe-agent-cli auth refresh
qwayk-xero-safe-agent-cli auth status --profile pkce
```

## Paid Custom Connection

This optional client-credentials flow is tied to one organisation.

- Uses `XERO_CUSTOM_CLIENT_ID` and `XERO_CUSTOM_CLIENT_SECRET`.
- Has separate token and tenant files.
- Discovers the bound organisation with `tenant custom-discover`.
- Runs tenanted fixed commands with global `--auth-profile custom`.
- Does not send a `xero-tenant-id` header.

## Xero App Store API

App Store billing and connection operations use a separate non-tenanted client-credentials token.

- Uses `XERO_APP_STORE_CLIENT_ID` and `XERO_APP_STORE_CLIENT_SECRET`.
- Requests only the explicitly supplied non-tenanted scopes, such as `marketplace.billing` or `app.connections`.
- Is selected automatically for fixed `app-store.*` commands.
- Never uses or selects an organisation tenant.

The `marketplace.billing` path is legacy-only. Xero deprecated XASS in March 2026, accepted no new apps after 4 December 2025, and required existing customers to migrate by 1 July 2026. Xero still documents the four endpoints in its API reference, but a fixed command does not prove live entitlement or behavior.

## Non-tenanted connection lookup

The fixed `identity.get-connections` command uses the client-credentials flow and the `app.connections` scope. It requires one exact documented target header, `Xero-Tenant-Id` or `Xero-User-Id`. It does not reuse the PKCE token or a selected tenant.

## Secret handling

Token status returns expiry, scopes, and whether a refresh token exists, but never token values. HTTP errors are reduced to safe messages. Bearer credentials, Basic credentials, token fields, authorization codes, and client secrets are redacted from normal output.
