# Troubleshooting

When Open Library does not return what you expected, start by checking the target, the API response, and the exact JSON error. For this public read tool, most fixes are about the request itself: a missing ID, an empty result, a changed public record, a timeout, or an API root override.

Do not guess from an empty list or a `null` result. Ask the agent to fetch the actual record, show the error type, and explain whether the data is missing or the request needs to change.

A good first troubleshooting ask is: "Read the Open Library error, explain what failed in plain English, and tell me the safest next check without inventing missing data."

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

Open Library uses public endpoints here. No auth failures are expected, but API behavior can change.
Keep calls low-volume and add throttling in callers if needed.
