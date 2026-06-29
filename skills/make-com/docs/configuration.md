# Configuration

Configuration means the private settings the tool needs before it can connect.

Most users only need one file: `.env`. This file stays on your machine and should never be committed.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Environment variables are settings the tool reads by name.

Use these Make-specific values:
- `MAKE_BASE_URL`
- `MAKE_API_TOKEN` (API token; sent as `Authorization: Token <value>`)
- `MAKE_TIMEOUT_S` (optional; default is 30)

The CLI also accepts `MAKE_ZONE_URL` as a base URL alias, but new setup should use `MAKE_BASE_URL` and `MAKE_API_TOKEN`.

Official Make API zones include `https://eu1.make.com`, `https://eu2.make.com`, `https://us1.make.com`, `https://us2.make.com`, `https://eu1.make.celonis.com`, and `https://us1.make.celonis.com`.

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.

For normal local use, `.env` is the easiest path.
