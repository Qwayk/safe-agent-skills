# Connect your ElevenLabs account

ElevenLabs needs a local API key before an agent can check voices, models, history, or account access.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small account or voices read before asking for audio generation or downloads.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill these values:
   - `ELEVENLABS_API_BASE_URL=https://api.elevenlabs.io`
   - `ELEVENLABS_API_KEY=<your ElevenLabs API key>`
   - `ELEVENLABS_TIMEOUT_S=30`

## Step 2: Get the API key

1. Sign in to ElevenLabs.
2. Open the API keys page at `https://elevenlabs.io/app/settings/api-keys`.
3. Create a new API key if you do not already have one.
4. Copy the key once and paste it into `.env` as `ELEVENLABS_API_KEY=...`.

Never paste the key into chat. The tool reads it from `.env`.

## Step 3: What to ask your AI agent (examples)

Ask your agent to start with a read-only check, then show a preview before any live generation or download.

- “Confirm the tool is connected, then list my voices and available models.”
- “Show my recent generation history before downloading anything.”
- “Draft a text-to-speech plan first, then only generate the audio after I approve.”
- “Check my ElevenLabs usage so I know whether I am close to my limits.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Invalid or expired ElevenLabs API key
- Network or permission restrictions in the connected account

Common error help lives in `docs/troubleshooting.md`.
