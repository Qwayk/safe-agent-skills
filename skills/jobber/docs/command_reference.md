# Command reference

Start with [connection setup](onboarding.md) or [a first read](quickstart.md). See [approval and recovery](safety_model.md) before changing a record.

## Get connected

```bash
qwayk-jobber-safe-agent-cli --output json onboarding [--no-write-env]
qwayk-jobber-safe-agent-cli --output json --version
```

## Check access and auth

```bash
qwayk-jobber-safe-agent-cli --output json auth check
qwayk-jobber-safe-agent-cli --output json auth authorize-url
qwayk-jobber-safe-agent-cli --output json auth token set --file token.json
qwayk-jobber-safe-agent-cli --output json auth token status
qwayk-jobber-safe-agent-cli --output json --apply --yes auth token refresh --refresh-token <refresh_token>
```

## Schema helpers

```bash
qwayk-jobber-safe-agent-cli --output json schema summary
qwayk-jobber-safe-agent-cli --output json schema queries
qwayk-jobber-safe-agent-cli --output json schema mutations
qwayk-jobber-safe-agent-cli --output json schema webhook-topics
```

## Read commands

Use the [coverage list](api_coverage.md) to find a named read.

Use one named subcommand at a time:

```bash
qwayk-jobber-safe-agent-cli --output json read clients --selection "nodes { id name } totalCount" --limit 10
```

Use the flags you need for the requested fields.
- `--args-json` to pass JSON arguments
- `--args-file` to load JSON args from file
- `--selection` to define GraphQL selection fields
- `--selection-file` for larger selections
- `--limit` for limit/first style paging

## Write commands

Save the preview first. Apply only after the user approves that exact plan. See [approval and recovery](safety_model.md) for high-risk or irreversible changes.

```bash
qwayk-jobber-safe-agent-cli --output json write clientCreate --args-json '{"input": {"firstName":"Acme","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json write clientCreate --args-json '{"input": {"firstName":"Acme","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json write clientCreate --args-json '{"input": {"firstName":"Acme","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'
```

Write options
- `--args-json`, `--args-file`, `--selection`, `--selection-file`
- `--plan-out` to save a plan
- `--plan-in` to apply from a plan
- `--receipt-out` to save an apply receipt
- `--apply --yes --plan-in <plan.json>` required for live apply
- `--ack-no-snapshot` for high-risk mutations that run without a before-state snapshot
- `--ack-irreversible` for irreversible mutations when apply is requested

## Webhook helpers

```bash
qwayk-jobber-safe-agent-cli --output json webhooks topics
qwayk-jobber-safe-agent-cli --output json webhooks verify-signature --body-file payload.json --header X-Jobber-Hmac-SHA256=<header>
qwayk-jobber-safe-agent-cli --output json webhooks verify-signature --body '{"id":"..." , "event":"CLIENT_CREATE"}' --header X-Jobber-Hmac-SHA256=<header>
```

## Run a CSV job

Each row uses a named action such as `read.clients` or `write.clientCreate`. In the checkout, start with `examples/jobs.csv` for a read preview or `examples/jobs_with_write.csv` for a preview that includes a write.

```bash
qwayk-jobber-safe-agent-cli --output json jobs run --file jobs.csv
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json jobs run --file jobs.csv
```

To execute a reviewed job, use the same file. The tool checks that the file hash still matches the plan. A job with writes needs the approved plan and `--yes`. Add the required [high-risk flags](safety_model.md) when they apply.

```bash
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json jobs run --file jobs.csv
```

## Check past runs

```bash
qwayk-jobber-safe-agent-cli --output json runs list --limit 20
qwayk-jobber-safe-agent-cli --output json runs show --run-id <run-id>
```

## Find the code

In `src/jobber_safe_agent_cli/`, `cli.py` defines the commands and flags, and `commands/` handles the work. `schema_registry.py` loads the list of named reads and writes. `config.py` reads settings, and `http.py` sends the requests. `runs.py`, `json_files.py` and `audit_log.py` save local records. `errors.py` defines the errors the CLI can report.
