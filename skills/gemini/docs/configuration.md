# Configuration

Most users need only `.env`.

```dotenv
GEMINI_API_KEY=replace-with-your-local-key
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_TIMEOUT_S=30
```

`GEMINI_API_BASE_URL` should stay on Google's official host unless you are testing a local mock.

Run artifacts are saved under `.state/runs/` next to the selected `--env-file` for write-capable commands.
