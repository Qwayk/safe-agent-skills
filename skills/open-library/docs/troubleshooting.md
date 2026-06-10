# Troubleshooting

## Command parsing

Use `--output json` and check the JSON error object.
Missing required flags or subcommands return `ok: false` with `error_type: ValidationError`.

## Empty results

Search endpoints may return many matches but page them with `--limit` and `--offset`.

## Timeouts

Increase `OPEN_LIBRARY_TIMEOUT_S` if responses are slow.

## Config issues

- If `.env` is missing, onboarding will create it.
- If `--config` JSON is invalid, the tool returns a parse error.
- Contact and user-agent values are optional.

## API behavior

This tool uses public Open Library endpoints. No auth failures are expected, but API behavior can change.
Keep calls low-volume and add throttling in callers if needed.
