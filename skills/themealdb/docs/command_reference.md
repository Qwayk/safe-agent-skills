# Command reference

Use this page when you need the exact TheMealDB command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--version`
- `--env-file .env`
- `--config tool-config.json`
- `--timeout-s 30`
- `--output json|text`
- `--verbose`
- `--log-file audit.jsonl`
- `--debug`

## Setup and health

- `qwayk-themealdb-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-themealdb-safe-agent-cli auth check`

## Reads

- `qwayk-themealdb-safe-agent-cli categories`
- `qwayk-themealdb-safe-agent-cli list categories`
- `qwayk-themealdb-safe-agent-cli list areas`
- `qwayk-themealdb-safe-agent-cli list ingredients`
- `qwayk-themealdb-safe-agent-cli search name --name "Arrabiata"`
- `qwayk-themealdb-safe-agent-cli search first-letter --letter a`
- `qwayk-themealdb-safe-agent-cli lookup id --meal-id 52772`
- `qwayk-themealdb-safe-agent-cli random`
- `qwayk-themealdb-safe-agent-cli filter ingredient --ingredient chicken_breast`
- `qwayk-themealdb-safe-agent-cli filter category --category Seafood`
- `qwayk-themealdb-safe-agent-cli filter area --area Canadian`

## Output notes

- `categories` returns a `categories` array.
- `list categories`, `list areas`, and `list ingredients` return an `items` array.
- `search`, `lookup`, `random`, and `filter` return a `meals` array.
- Not-found search and filter results return an empty `meals` array with `count: 0`.

## Config JSON example

The optional `--config` file is a plain JSON object:

```json
{
  "base_url": "https://www.themealdb.com/api/json/v1",
  "timeout_s": 30
}
```
