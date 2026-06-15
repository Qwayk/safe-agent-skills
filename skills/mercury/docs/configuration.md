# Configuration

Mercury configuration is the local setup an agent needs before it can review accounts, transactions, recipients, cards, and banking activity. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Mercury values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.
