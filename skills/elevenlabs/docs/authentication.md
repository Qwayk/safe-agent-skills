# Authentication

The CLI uses an ElevenLabs API key from `ELEVENLABS_API_KEY` and sends it as the `xi-api-key` header. It does not use OAuth login for this integration.

Keep the key in a local, gitignored `.env` file. Never paste it into chat, prompts, plans, receipts, logs, or command output.

```text
ELEVENLABS_API_KEY=<your ElevenLabs API key>
ELEVENLABS_API_BASE_URL=https://api.elevenlabs.io
ELEVENLABS_TIMEOUT_S=30
```

Create or rotate keys at [ElevenLabs API keys](https://elevenlabs.io/app/settings/api-keys). A plan-only auth check reads local configuration and does not contact the provider. To test the credential, run:

```text
elevenlabs-api-tool --output json --env-file .env --live auth check --out ./auth.json --overwrite
```

The sensitive provider response is written to `auth.json`; stdout reports only safe metadata. If the response is `401` or `403`, check the key, workspace, and permissions without exposing the key. See [configuration](configuration.md) for env-file behavior.
