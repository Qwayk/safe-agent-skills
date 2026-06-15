# Configuration

Hacker News configuration is light because the default work uses public data. Set local values only when you want to change the API root, timeout, contact details, or another default for public story lists, items, comments, users, and recent updates.

There is no private secret to paste into chat. If you do add a local `.env` or `--env-file`, use it for settings like timeouts or contact fields, not credentials.

A good first configuration check is: "Show me the Hacker News defaults, tell me which values I can change, and confirm the setup without asking for secrets."

## Where settings come from

Settings can come from:
- a `.env` file specified by `--env-file` (default: `.env`)
- an optional JSON config file specified by `--config`
- OS environment variables override values from the env file

CLI flags override file and environment settings:
- `--api-root` overrides `HACKER_NEWS_API_ROOT`
- `--timeout-s` overrides `HACKER_NEWS_TIMEOUT_S`

## Required

Nothing is required for the default public API.

If you want to pin or override the API root, use:
- `HACKER_NEWS_API_ROOT` (default: `https://hacker-news.firebaseio.com/v0`)

## Optional

- `HACKER_NEWS_TIMEOUT_S` (seconds; default: `30`)

## JSON config file

Example `config.json`:

```json
{
  "api_root": "https://hacker-news.firebaseio.com/v0",
  "timeout_s": 30
}
```
