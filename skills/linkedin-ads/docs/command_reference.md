# LinkedIn Ads commands

Use the [quickstart](quickstart.md) for a complete setup, report, and campaign plan. The [coverage table](api_coverage.md) lists every command family and its access requirements.

## Setup and account access

- `linkedin-ads-api-tool --output json --version` shows the installed CLI version.
- `linkedin-ads-api-tool --output json onboarding` creates the local settings file if it is missing.
- `linkedin-ads-api-tool --output json auth token set --file token.json` saves a token from a local JSON file.
- `linkedin-ads-api-tool --output json auth token status` shows the saved file's status.
- `linkedin-ads-api-tool --output json auth check` asks LinkedIn which account roles the signed-in member has.
- `linkedin-ads-api-tool --output json ad-account-users list-authenticated-user` lists the account roles again.

## Read or plan a change

The command shape is `linkedin-ads-api-tool [global options] <family> <operation> [operation options]`. Put global options such as `--output json`, `--env-file`, `--plan-out`, `--plan-in`, and `--receipt-out` before the family name.

- Use `--param key=value` for each query parameter. Quote list and date values as shown in the [report example](quickstart.md#read-campaign-results).
- Use `--body-json '<json>'` or `--body-file path` for requests that take a JSON body.
- Path fields become command options. For example, `{ad_account_id}` becomes `--ad-account-id`.
- Use `--plan-out path` to save a write plan. Follow the [approval guide](safety_model.md) before applying it.
- Use `--receipt-out path` to save the response receipt after the tool sends a change. Check the affected item separately to confirm its state.
- Use `--verbose` to see the request line and timing on stderr.

## Local run history

- `linkedin-ads-api-tool runs list [--limit N]` shows recent runs.
- `linkedin-ads-api-tool runs show --run-id <id>` shows the saved run.
- `--run-id` sets a run ID. `--artifacts-dir` sets its location.

Write commands normally save run files under `.state/runs/<run_id>/` and add a line to `.state/runs/index.jsonl`. Keep run files private if they contain account or campaign data.
