# Configuration

This tool reads configuration from:
- a `.env` file specified by `--env-file` (default: `.env`)
- an optional JSON config file specified by `--config`
- OS environment variables override values from the env file

CLI flags override everything:
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
