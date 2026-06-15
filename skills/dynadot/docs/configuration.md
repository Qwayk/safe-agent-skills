# Configuration

Dynadot configuration is the local setup an agent needs before it can inspect domains, DNS records, nameservers, and account domain data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Dynadot values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local run artifacts (gitignored)

## Environment variables

Required:
- `DYNADOT_API_KEY`: your Dynadot API key.

Recommended (defaults are fine for most users):
- `DYNADOT_API_BASE_URL`: defaults to `https://api.dynadot.com/api3.json`
- `DYNADOT_TIMEOUT_S`: defaults to `30`

Optional:
- `DYNADOT_API_SANDBOX_BASE_URL`: not used automatically yet; reserved for future `--sandbox` support.

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
