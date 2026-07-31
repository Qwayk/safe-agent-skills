# Configuration

Configuration is local file settings plus optional environment overrides.

Most users only need one file: `.env`.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.env` supplies local values. Matching operating-system environment variables take precedence.

OAuth tokens are generated at runtime and kept in memory only for that process.

## Environment variables

Use these exact names:
- `NAMEBRIGHT_CLIENT_ID`
- `NAMEBRIGHT_CLIENT_SECRET`
- `NAMEBRIGHT_TIMEOUT_S` (optional)

## Scope and limits

- `NAMEBRIGHT_CLIENT_ID` and `NAMEBRIGHT_CLIENT_SECRET` are the only required values.
- The tool does not support API base URL overrides.
- OS environment values may override `.env` file values.
