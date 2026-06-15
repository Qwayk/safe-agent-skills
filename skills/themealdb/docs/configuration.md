# Configuration

TheMealDB configuration is light because the default work uses public data. Set local values only when you want to change the API root, timeout, contact details, or another default for public meals, recipes, ingredients, categories, and areas.

There is no private secret to paste into chat. If you do add a local `.env` or `--env-file`, use it for settings like timeouts or contact fields, not credentials.

A good first configuration check is: "Show me the TheMealDB defaults, tell me which values I can change, and confirm the setup without asking for secrets."

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
