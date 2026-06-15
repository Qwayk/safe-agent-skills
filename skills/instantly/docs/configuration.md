# Configuration

Instantly configuration is the local setup an agent needs before it can review campaigns, leads, accounts, replies, and outreach performance. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Instantly values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/runs/`: local run artifacts for write-capable commands (gitignored; lives next to your `--env-file`)

## Environment variables

- `INSTANTLY_API_BASE_URL` (optional; default: `https://api.instantly.ai/api/v2`)
- `INSTANTLY_API_KEY` (required; Instantly API key)
- `INSTANTLY_TIMEOUT_S` (optional; default: `30`)

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
