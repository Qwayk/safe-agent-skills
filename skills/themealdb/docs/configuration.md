# Configuration

## Environment variables

- `THEMEALDB_BASE_URL`
  - Default: `https://www.themealdb.com/api/json/v1`
- `THEMEALDB_API_KEY`
  - Default: `1`
- `THEMEALDB_TIMEOUT_S`
  - Default: `30`

## Optional JSON config

You can pass non-secret defaults with `--config`:

```json
{
  "base_url": "https://www.themealdb.com/api/json/v1",
  "timeout_s": 30
}
```

## Precedence

Highest to lowest:

1. CLI `--timeout-s`
2. OS environment variables
3. `.env` file
4. `--config` JSON file
5. Built-in defaults
