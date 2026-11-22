# Command reference

Use this page to find the command and flags for your project, job, report or metric. Start with the [quickstart](quickstart.md) for your first read. In JSON mode, a command prints one JSON object. See [approvals and receipts](safety_model.md) before sending a change.

## Setup

- `contentsquare-safe-cli onboarding`
- `contentsquare-safe-cli auth check`
- `contentsquare-safe-cli auth check --scope metrics`
- `contentsquare-safe-cli --oauth-project-id 42 auth check`
- `contentsquare-safe-cli auth me`
- `contentsquare-safe-cli runs list`
- `contentsquare-safe-cli runs show --run-id <run_id>`

See [setup](onboarding.md) for settings, OAuth scopes and how to select a project.

## Data Export

- `contentsquare-safe-cli data-export create-job --body-json body.json`
- `contentsquare-safe-cli data-export list-jobs --state COMPLETED --order DESC --format CSV --frequency daily --scope-filter views --page 1 --limit 25`
- `contentsquare-safe-cli data-export list-successful-runs --page 1 --limit 25`
- `contentsquare-safe-cli data-export get-job --job-id 123`
- `contentsquare-safe-cli data-export list-runs --job-id 123 --state SUCCESS --page 1 --limit 25`
- `contentsquare-safe-cli data-export get-run --job-id 123 --run-id-value 77`
- `contentsquare-safe-cli data-export exportable-fields --scope-filter sessions`
- `contentsquare-safe-cli data-export custom-vars`
- `contentsquare-safe-cli data-export dynamic-var-keys --from 2026-06-01T00:00:00Z --to 2026-06-07T00:00:00Z`
- `contentsquare-safe-cli data-export download-run-file --job-id 123 --run-id-value 77 --file-index 0 --output-file export.ndjson`

`--scope-filter` is the export filter sent as `scope`. The separate `--scope` flag is for OAuth. Date filters `--from` and `--to` use the same names in Contentsquare's API.

An accepted `create-job` reply gives a command to list runs when Contentsquare returns the job ID. Use `get-run` to see the run's reported state and whether it has download links. For example, `RUNNABLE` means it is waiting to start, and `SUCCESS` means it finished. See [Contentsquare's export states](https://docs.contentsquare.com/en/api/export/enumerations/).

`download-run-file` first reads `GET /v1/exports/{jobId}/runs/{runId}` and uses the URL in `files[].url`. If there is more than one file, choose with `--file-index` (starting at zero) or `--part-id`. Download before the link expires. The CLI checks the download before saving it. Pass `--overwrite` when you intend to replace the file.

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

These commands read reports or lists. They use POST to send the report options in a JSON file.

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

Preview the event, then apply the saved plan after approval:

```bash
contentsquare-safe-cli --plan-out event-plan.json speed-analysis event-create --body-json event.json
contentsquare-safe-cli --plan-in event-plan.json --apply --yes --ack-no-snapshot speed-analysis event-create
```

For a delete, use the extra confirmation for an action you can't undo:

```bash
contentsquare-safe-cli --plan-out delete-plan.json speed-analysis event-delete --body-json event-to-delete.json
contentsquare-safe-cli --plan-in delete-plan.json --apply --yes --ack-irreversible speed-analysis event-delete
```

## Where the code handles each step

`catalog.py` lists the documented operations and `cli.py` turns them into commands. `config.py` and `project_config.py` read local settings. `contentsquare_client.py` gets the token and sends requests through `http.py`. `commands/contentsquare.py` checks plans, records replies and handles export downloads. `errors.py`, `output.py`, `audit_log.py` and `runs.py` handle errors, results and saved run records.
