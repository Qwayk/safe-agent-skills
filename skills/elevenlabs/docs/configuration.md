# Configuration

This tool uses a `.env` file for configuration. Do not commit `.env`.

## Files

- `.env.example`: copy this to `.env` (local-only).
- `.state/`: the local state directory that sits beside the chosen `--env-file` (gitignored).
  - `runs/index.jsonl`: per-run index for tracking, appended on every dry-run/apply.
  - `runs/<run_id>/audit.jsonl`: individual run audit entries that the CLI writes when it executes.

State files always live in the same folder as the selected `--env-file` so you can treat the directory as a single, portable workspace.

## Environment variables

Set these values for your ElevenLabs workspace:

- `ELEVENLABS_API_BASE_URL` — usually `https://api.elevenlabs.io`.
- `ELEVENLABS_API_KEY` — the `xi-api-key` value from https://elevenlabs.io/app/settings/api-keys.
- `ELEVENLABS_TIMEOUT_S` — optional request timeout in seconds (default: 30).

OS environment variables override the same keys from the env file (handy for CI or containers).
