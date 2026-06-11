# Authentication (Freepik API)

This tool uses a Freepik API key.

It never prints your API key, and it never prints HTTP `Authorization` headers.

## Required

- `FREEPIK_API_KEY`: your Freepik API key.

Create a local env file:

1) Copy `.env.example` → `.env` in the tool repo root
2) Set `FREEPIK_API_KEY=...`
3) Do **not** commit `.env` (it is gitignored)

Smoke check:

```bash
freepik-api-tool --output json auth check
```

## Header details (advanced / rarely needed)

By default, the tool sends the Freepik API key in the header `x-freepik-api-key`.

If Freepik changes their auth header in the future (or you’re using a proxy), you can override:

- `FREEPIK_AUTH_HEADER` (default: `x-freepik-api-key`)
- `FREEPIK_AUTH_PREFIX` (default: empty)

Example (prefix-based auth):

```bash
FREEPIK_AUTH_HEADER=Authorization
FREEPIK_AUTH_PREFIX='Bearer '
```
