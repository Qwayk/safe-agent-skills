# Onboarding (non-technical)

This tool runs on your computer and connects to ElevenLabs using an API key that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview, or with a safe refusal when a write is blocked.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

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

These are plain-English requests. The agent should start with a read-only check, then show a preview before any live generation or download.

- “Confirm the tool is connected, then list my voices and available models.”
- “Show my recent generation history before downloading anything.”
- “Draft a text-to-speech plan first, then only generate the audio after I approve.”
- “Check my ElevenLabs usage so I know whether I am close to my limits.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Invalid or expired ElevenLabs API key
- Network/auth restrictions in the vendor account

Common error help lives in `docs/troubleshooting.md`.
