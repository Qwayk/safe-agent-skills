# Command reference

Use this page when you need the exact Salesforce Platform command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Setup and auth

- `qwayk-salesforce-platform-safe-agent-cli --output json --version`
- `qwayk-salesforce-platform-safe-agent-cli onboarding`
- `qwayk-salesforce-platform-safe-agent-cli auth check`
- `qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json`
- `qwayk-salesforce-platform-safe-agent-cli auth token status`

## Common helpers

- `--query-param key=value`
  - for less common documented query parameters that are not first-class CLI flags
- `--header key=value`
  - for headers like `Accept-Language`
  - the tool refuses manual `Authorization`, `Accept`, and `Content-Type`
- `--download-to path`
  - save CSV or binary responses to a file
- `--body-file path`
  - JSON request body
- `--data-file path`
  - raw upload file, mainly for Bulk API 2.0 ingest CSV uploads
- `--multipart-file path`
  - multipart manifest for documented blob-upload flows

## Write-safety helpers

- `--apply`
- `--yes`
- `--ack-irreversible`
- `--plan-out path`
- `--plan-in path`
- `--receipt-out path`

Salesforce write plans are reviewable before apply. Apply still checks required flags and plan drift. When no useful before-state can be saved, it requires explicit no-snapshot approval before Salesforce HTTP and the receipt must record that recovery limit.

Salesforce write plans are explicit about the current no-recovery contract:
- no automatic rollback,
- no snapshots,
- no backups,
- no generated `rollback_plan`.
They also include `before_state.required: true` and `before_state.supported: false` for write operations.

## Run history

- `qwayk-salesforce-platform-safe-agent-cli runs list --limit 20`
- `qwayk-salesforce-platform-safe-agent-cli runs show --run-id 2026-01-19T104512Z_a3f91c`

## Common examples

Read available resources:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json resources list
```

Run a SOQL query:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
```

Describe an object:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json sobjects-describe get --sobject Account
```

Read Knowledge articles in a specific language:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json support knowledge-articles --header Accept-Language=en-US --query-param channel=Pkb
```

Preview a composite write:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json composite execute --body-file composite.json --plan-out plan.json
```

Request apply for that composite write. This currently requires explicit no-snapshot approval before Salesforce HTTP when the tool cannot save real before-state:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json --apply --yes --plan-in plan.json composite execute --body-file composite.json
```

Create an ingest job, then upload CSV:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json jobs-ingest create --body-file ingest-job.json
qwayk-salesforce-platform-safe-agent-cli --output json jobs-ingest upload --job-id 750... --data-file rows.csv
```

Generate the sObjects OpenAPI document beta:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json openapi-sobjects create --body-file openapi-request.json
```

Blob upload preview with multipart manifest:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json sobjects-object create --sobject Document --multipart-file multipart.json
```

For the full shipped family and action ledger, use `docs/api_coverage.md`.
