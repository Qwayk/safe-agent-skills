# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local run artifacts (gitignored; written next to your `--env-file`)

## Environment variables

- `MERCURY_API_BASE_URL`
- `MERCURY_API_TOKEN` (Mercury API token)
- `MERCURY_AUTH_SCHEME` (`bearer` or `basic`; default: `bearer`)
- `MERCURY_TIMEOUT_S` (optional; default is 30)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
