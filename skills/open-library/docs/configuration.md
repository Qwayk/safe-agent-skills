# Configuration

This tool reads values from `.env` by default.

Supported settings:

- `OPEN_LIBRARY_BASE_URL` (default: `https://openlibrary.org`)
- `OPEN_LIBRARY_TIMEOUT_S` (default: `30`)
- `OPEN_LIBRARY_USER_AGENT_APP` (default: `qwayk-open-library-safe-agent-cli`)
- `OPEN_LIBRARY_CONTACT` (optional)

You can also place these values in a JSON file and pass it with `--config`:

```json
{
  "base_url": "https://openlibrary.org",
  "timeout_s": 30,
  "user_agent_app": "qwayk-open-library-safe-agent-cli",
  "contact": "you@example.com"
}
```

`--config` values are optional and can override values from `.env`.

Notes:
- OS environment values are still loaded through the normal environment lookup and `.env` file path used by `--env-file`.
