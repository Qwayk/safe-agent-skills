# Authentication

Every provider request uses an already-issued bearer token over HTTPS to Asana's official REST server:

```text
https://app.asana.com/api/1.0
```

## Personal access token

A personal access token is the simplest default. It acts as the Asana user who created it and can reach only data that user can reach. Store it as `ASANA_ACCESS_TOKEN` in the OS environment or private `.env` file.

## OAuth access token

An OAuth access token uses the same `Authorization: Bearer` transport. The fixed command metadata preserves official OAuth scopes, which you can inspect with:

```bash
asana-safe commands show get-tasks-for-project
```

The tool does not register an app, open an authorization page, exchange a code, refresh or revoke a token, request OpenID Connect data, or store OAuth token JSON. Obtain and maintain the token outside this CLI.

## Service-account token

Asana service accounts also use bearer transport. Only service-account-enabled organizations and operations will accept them. AI Studio usage, audit logs, exports, and other gated areas may have separate plan, admin, or service-account requirements.

## Connection check

`asana-safe auth check` calls the fixed `/users/me` read and returns only GID, name, and resource type. A 401 means the token is missing, invalid, expired, or revoked. A 403 on another command normally means the token is valid but lacks access to that target or operation.

Tokens are never printed in normal output, plans, receipts, audit logs, or errors.
