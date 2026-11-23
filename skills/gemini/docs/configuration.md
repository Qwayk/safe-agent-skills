# Local settings

[First-time setup](onboarding.md) creates the settings file. `GEMINI_API_KEY` is the only required entry. A value in your shell takes priority over the same entry in the file.

The optional settings are:

```dotenv
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_TIMEOUT_S=30
```

Use Google’s default address for Gemini and a test address only with a test key. The timeout is in seconds. You can set it for one command with `--timeout-s`.

Plan and receipt files normally go under `.state/runs/` beside the selected settings file. The tool also records which saved plans have already been sent there.
