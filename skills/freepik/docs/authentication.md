# Authentication

Freepik authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because image search, licensed downloads, binary fetches, and local inventory files can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Freepik environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

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
