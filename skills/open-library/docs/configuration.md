# Configuration

Open Library configuration is light because the default work uses public data. Set local values only when you want to change the API root, timeout, contact details, or another default for public books, authors, editions, subjects, and ISBN data.

There is no private secret to paste into chat. If you do add a local `.env` or `--env-file`, use it for settings like timeouts or contact fields, not credentials.

A good first configuration check is: "Show me the Open Library defaults, tell me which values I can change, and confirm the setup without asking for secrets."

## Where settings come from

Settings come from `.env` by default.

## Supported settings

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

## Notes
- OS environment values are still loaded through the normal environment lookup and `.env` file path used by `--env-file`.
