# Onboarding

You need a Gemini API key from Google AI Studio. The tool reads the key from your local `.env` file and never needs the key pasted into chat.

## Steps

1. Open [Google AI Studio](https://aistudio.google.com/) and create or copy a Gemini API key.
2. In this tool folder, run `cp .env.example .env`.
3. Edit `.env` and set `GEMINI_API_KEY`.
4. Run `gemini-api-tool --output json auth check`.
5. Run `gemini-api-tool --output json models list`.

`GEMINI_API_BASE_URL` normally stays `https://generativelanguage.googleapis.com`.

## Access

The official Gemini API uses the `x-goog-api-key` header for normal REST calls. Discovery also lists an OAuth storage read-only scope for some upload-style flows, but this source-ready CLI defaults to API-key auth because that is the normal documented Gemini path.

## First Ask For An Agent

"Use the Gemini skill to list available models, then recommend one for long document review with structured JSON."
