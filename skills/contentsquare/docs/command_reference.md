# Command reference

Use the command reference when you already know the Contentsquare project, mapping, page group, zoning, zone, job, or report ID you want to query and need the exact command shape, body file, or safety flag.

For the guided path, start with [Good first asks](use_cases.md), [Set up your account step by step](onboarding.md), and [Understand the safety checks](safety_model.md). All JSON mode commands print one JSON object.

## Setup

- `contentsquare-safe-cli onboarding`
- `contentsquare-safe-cli auth check`
- `contentsquare-safe-cli auth check --scope metrics`
- `contentsquare-safe-cli --oauth-project-id 42 auth check`
- `contentsquare-safe-cli auth me`
- `contentsquare-safe-cli runs list`
- `contentsquare-safe-cli runs show --run-id <run_id>`

`auth check` defaults to the official `data-export` OAuth scope. API commands use their own documented family scope automatically: `data-export`, `metrics`, `enrichment`, or `speed-analysis`. Use `--scope` only when you intentionally need an official override. Use `--oauth-project-id` or `CONTENTSQUARE_PROJECT_ID` when account-level OAuth credentials need the documented token `project_id`.

## Data Export

- `contentsquare-safe-cli data-export create-job --body-json body.json`
- `contentsquare-safe-cli data-export list-jobs --state completed --order DESC --format CSV --frequency daily --scope-filter views --page 1 --limit 25`
- `contentsquare-safe-cli data-export list-successful-runs --page 1 --limit 25`
- `contentsquare-safe-cli data-export get-job --job-id job_123`
- `contentsquare-safe-cli data-export list-runs --job-id job_123 --state completed --page 1 --limit 25`
- `contentsquare-safe-cli data-export get-run --job-id job_123 --run-id-value run_123`
- `contentsquare-safe-cli data-export exportable-fields --scope-filter sessions`
- `contentsquare-safe-cli data-export custom-vars`
- `contentsquare-safe-cli data-export dynamic-var-keys --from 2026-06-01T00:00:00Z --to 2026-06-07T00:00:00Z`
- `contentsquare-safe-cli data-export download-run-file --job-id job_123 --run-id-value run_123 --file-index 0 --output-file export.ndjson`

The CLI keeps friendly flag names, but the API request uses Contentsquare's documented query names. For example `--scope-filter` is sent as `scope`, `--from` is sent as `from`, and `--to` is sent as `to`. `download-run-file` first reads `GET /v1/exports/{jobId}/runs/{runId}` and downloads only a documented `files[].url`. If the run has more than one file, choose with `--file-index` or `--part-id`.

## Metrics

Object commands:

- `contentsquare-safe-cli metrics segments --project-id 123`
- `contentsquare-safe-cli metrics segments --project-id 123 --ids 10,11`
- `contentsquare-safe-cli metrics goals --project-id 123`
- `contentsquare-safe-cli metrics mappings --project-id 123`
- `contentsquare-safe-cli metrics mapping --mapping-id 456`
- `contentsquare-safe-cli metrics page-groups --mapping-id 456`
- `contentsquare-safe-cli metrics page-group --page-group-id 789`
- `contentsquare-safe-cli metrics zonings --page-group-id 789`
- `contentsquare-safe-cli metrics zones --zoning-id 987`

Site metric commands use `metrics site <name>`.

Page group metric commands use `metrics page-group-metric <name> --page-group-id 789`.

Zone web metric commands use `metrics zone-web <name> --zone-id 654`.

Zone app metric commands use `metrics zone-app <name> --zone-id 654`.

Each metric read accepts common filters such as `--project-id`, `--start-date`, `--end-date`, `--segment-id`, `--segment-ids`, `--goal-id`, `--device`, and `--period` when the provider endpoint supports them. The actual API request uses Contentsquare's documented names: `projectId`, `startDate`, `endDate`, `segmentIds`, `goalId`, `ids`, `device`, and `period`.

## Enrichment

Dry-run:

```bash
contentsquare-safe-cli --plan-out enrichment-plan.json enrichment send-batch --integration-id integration_123 --body-json batch.json
```

Apply after review:

```bash
contentsquare-safe-cli --plan-in enrichment-plan.json --apply --yes --ack-no-snapshot --receipt-out enrichment-receipt.json enrichment send-batch --integration-id integration_123
```

## Speed Analysis Lab

Read-style POST commands:

- `speed-analysis analysis-report --body-json body.json`
- `speed-analysis analysis-har --body-json body.json`
- `speed-analysis monitoring-list --body-json body.json`
- `speed-analysis monitoring-last-report --body-json body.json`
- `speed-analysis monitoring-reports --body-json body.json`
- `speed-analysis scenario-list --body-json body.json`
- `speed-analysis scenario-report --body-json body.json`
- `speed-analysis scenario-reports --body-json body.json`
- `speed-analysis scenario-step-report --body-json body.json`
- `speed-analysis scenario-report-har --body-json body.json`
- `speed-analysis event-list --body-json body.json`

Event writes are dry-run first:

```bash
contentsquare-safe-cli --plan-out event-plan.json speed-analysis event-create --body-json event.json
contentsquare-safe-cli --plan-in event-plan.json --apply --yes --ack-no-snapshot speed-analysis event-create
```

Delete requires both acknowledgements:

```bash
contentsquare-safe-cli --plan-in delete-plan.json --apply --yes --ack-no-snapshot --ack-irreversible speed-analysis event-delete
```
