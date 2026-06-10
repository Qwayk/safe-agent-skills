# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## API key problems

- If `auth check` says `Missing ELEVENLABS_API_KEY`, open `.env` and paste a real ElevenLabs API key.
- If ElevenLabs returns `401` or `403`, rerun `auth check` with `--live --out ./auth.json --overwrite` (plan-only never contacts ElevenLabs, so the live flag is required to hit the service). The tool stays file-only, fingerprinting stdout, and `auth.json` holds the exact ElevenLabs error.
- Keep using `.env` only. Do not paste the key into command history or chat.
