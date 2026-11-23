# Set up Gemini

You need Python 3.12 or later and a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

Open the [Gemini tool’s source folder](https://github.com/Qwayk/safe-agent-skills/tree/main/skills/gemini). Install the CLI from that folder and create your local settings file:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/gemini-api-tool onboarding
```

Open `.env` and replace the placeholder with your key. Keep the file private and out of Git. A key set in your shell takes priority over the file. Run:

```bash
.venv/bin/gemini-api-tool --output json auth check
.venv/bin/gemini-api-tool --output json models list
```

`auth check` checks for a key on your computer. `models list` asks Google which models that key can use.

For a different settings path, pass `--env-file "path/to/settings.env"` before `onboarding`. The tool creates a private starter file if it’s missing and shows both commands with your path. Use `onboarding --no-write-env` if you only want the instructions. [Settings and defaults](configuration.md)

## If you get stuck

- **Missing key.** Open the file named in the setup output. Replace the placeholder, or set `GEMINI_API_KEY` in your shell.
- **Google rejects the request.** Check the key and project in Google AI Studio, then try `models list` again.
- **You need the full error while fixing the code.** Use `--debug` on your computer and check the output for private details before sharing it.

Gemini requests use the API key in the `x-goog-api-key` header. The local OAuth helpers `auth token status` and `auth token set --file token.json` manage a file on your computer. The Gemini commands use the API key.
