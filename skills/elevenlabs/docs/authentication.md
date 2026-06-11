# Authentication

The tool authenticates with ElevenLabs using the `xi-api-key` header and the `ELEVENLABS_API_KEY` value stored in `.env`.

```
ELEVENLABS_API_KEY=call_{redacted}
ELEVENLABS_API_BASE_URL=https://api.elevenlabs.io
ELEVENLABS_TIMEOUT_S=30
```

Onboarding steps:

1. Visit https://elevenlabs.io/app/settings/api-keys to create or copy an ElevenLabs API key.
2. Paste the key into `.env` under `ELEVENLABS_API_KEY` and keep the file gitignored.
3. Run `elevenlabs-api-tool --output json --env-file .env.example auth check` to validate your local configuration (plan-only means the CLI only reads `.env` and never contacts ElevenLabs, so plan failures don’t reflect credential problems).
   - To confirm the API key works, rerun with `--live --out ./auth.json --overwrite` so the CLI writes the sensitive ElevenLabs response to disk and stdout only prints the fingerprint; the file will include `ok=false` plus the provider error when the key or scopes are wrong.

If ElevenLabs introduces region-specific hosts, override `ELEVENLABS_API_BASE_URL` before rerunning the `auth check`.

Important reminders:
- Never log `.env` contents or the `xi-api-key` header.
- Auth failures should only report safe messages (no stack traces unless `--debug`).
