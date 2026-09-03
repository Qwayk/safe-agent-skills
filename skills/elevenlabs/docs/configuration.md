# Configuration

Configuration is loaded from the selected `--env-file` (normally `.env`); process environment variables override values from that file.

Required for live provider calls:

- `ELEVENLABS_API_KEY`: the ElevenLabs `xi-api-key` value.
- `ELEVENLABS_API_BASE_URL`: normally `https://api.elevenlabs.io`.

Optional:

- `ELEVENLABS_TIMEOUT_S`: request timeout in seconds; default `30`.

Copy `.env.example` to `.env` and keep `.env` local-only. `.state/runs/` stores local run indexes and audit artifacts beside the selected env file; it must not contain secrets.

The safest configuration check is plan-only:

```text
elevenlabs-api-tool --output json --env-file .env.example auth check
```

Use `--live` only when current provider data is wanted. Binary and sensitive results require `--out <path>`.
