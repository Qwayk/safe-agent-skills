# Troubleshooting

When ElevenLabs stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent checking voices, usage, models, and text-to-speech setup, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the ElevenLabs error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
