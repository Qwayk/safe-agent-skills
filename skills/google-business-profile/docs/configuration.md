# Configuration

This tool uses `.env` for local configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/oauth_credentials.json`: OAuth credentials written by `auth login` (gitignored)

Auth credentials are stored in `.state/` next to `--env-file`.

## Environment variables

This slice uses:
- `GBP_OAUTH_CLIENT_SECRETS_FILE`
- `GBP_OAUTH_SCOPES` (optional; defaults to `https://www.googleapis.com/auth/business.manage`)
- `GBP_TIMEOUT_S` (optional; default is `30`)

## Scope of configuration

Fixed API endpoints are kept in source code for this foundation slice.
This slice uses these official hosts only:
- `https://mybusinessaccountmanagement.googleapis.com`
- `https://mybusinessbusinessinformation.googleapis.com`
- `https://mybusinessbusinesscalls.googleapis.com`
- `https://mybusinessnotifications.googleapis.com`
- `https://mybusiness.googleapis.com`
- `https://mybusinessplaceactions.googleapis.com`
- `https://mybusinesslodging.googleapis.com`
- `https://businessprofileperformance.googleapis.com`
- `https://mybusinessverifications.googleapis.com`

## OS environment override

OS environment variables override values from the `.env` file.
This is useful in CI or container workflows.
