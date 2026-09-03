# Connect your ElevenLabs account

This CLI reads an ElevenLabs API key from a local `.env` file. Start with a plan-only command; add `--live` only when you intend to contact ElevenLabs.

Keep `.env`, API keys, OAuth material, audio, transcripts, and saved response files out of chat and Git.

## Setup

From the tool folder:

1. Copy `.env.example` to `.env`.
2. Set `ELEVENLABS_API_KEY` to a key created at [ElevenLabs API keys](https://elevenlabs.io/app/settings/api-keys).
3. Keep `ELEVENLABS_API_BASE_URL=https://api.elevenlabs.io` and `ELEVENLABS_TIMEOUT_S=30` unless your environment requires another value.

The key is sent as the `xi-api-key` header. It is never printed by the CLI.

## First checks

Use a local plan to confirm command syntax:

```text
elevenlabs-api-tool --output json --env-file .env.example auth check
```

To check the real account, use `--live` and keep the sensitive response in a file:

```text
elevenlabs-api-tool --output json --env-file .env --live auth check --out ./auth.json --overwrite
```

Then ask your agent to list voices or models. Generation, transcription, music, voice design, and calls can spend credits or affect real people; review the plan and required approvals first.

## If setup fails

Check the env-file path, key validity and workspace permissions. A plan-only run cannot validate a credential against ElevenLabs. See [authentication](authentication.md) and [troubleshooting](troubleshooting.md).
