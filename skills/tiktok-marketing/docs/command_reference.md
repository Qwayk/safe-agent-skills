# TikTok Marketing commands

Use the [quickstart](quickstart.md) for full examples of setup, reporting, and a campaign pause. The [coverage table](api_coverage.md) lists all 240 named API commands.

## Setup and accounts

- `tiktok-marketing-api-tool --output json onboarding` creates your settings file if it is missing. Add `--no-write-env` after `onboarding` to check setup without creating the file.
- `tiktok-marketing-api-tool --output json auth check` asks TikTok which ad accounts are available.
- `tiktok-marketing-api-tool --output json auth token set --file token.json` saves an access token from a local file.
- `tiktok-marketing-api-tool --output json auth token status` checks whether the saved file is present.

## Find and use an API command

- `api ops list` lists available operations. Add `--method GET` or `--family campaign` to narrow the list.
- `api ops show --op report-integrated-get` shows what one operation accepts.
- `api <operation>` prepares a plan. `--live api <operation>` sends a read. Follow the [approval guide](safety_model.md) for writes.
- Use `--query-json` or `--body-json` for inline JSON or the path to a JSON file. Use `--query key=value` for one query field and `--file field=path` for a supported upload field.

## Options that go before the command

- `--output json` gives one JSON result. `--version` shows the installed version.
- `--env-file`, `--config`, `--project-dir`, and `--timeout-s` choose local settings and the request timeout.
- `--live` enables provider calls. Writes also need `--apply --yes --plan-in plan.json --ack-irreversible --ack-no-snapshot` when the old settings cannot be saved.
- `--plan-out` saves a plan. `--receipt-out` saves the provider response record.
- `--verbose` shows request timing. `--debug` shows error details for local debugging. `--log-file` adds a local log.
- `--run-id`, `--artifacts-dir`, and `--no-artifacts` control local run files.

## Local run history

Use `runs list --limit 20` to find a recent run and `runs show --run-id <id>` to read it. Local run files usually live in `.state/runs/` next to the settings file.
