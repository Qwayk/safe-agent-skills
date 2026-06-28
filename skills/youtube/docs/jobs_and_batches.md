# Jobs and batches

Use this page when you want to test repeatable CSV jobs or understand the current batch limits.

Batch operations are run from a CSV file:

```bash
youtube-api-tool jobs run --file jobs.csv
```

## Safety rules

- Jobs are strict by default.
- Without `--apply`, jobs run in dry-run mode and include a plan for write rows.
- Any write row starts as a plan first.
- The runner stops on the first error and exits non-zero.
- Write rows are safety examples today. Apply attempts return a refusal instead of performing real YouTube writes.
- Output is exactly one JSON summary object.

## Plan files (recommended for risky jobs)

If a jobs run includes writes, prefer:

1) Create a plan file (dry-run):

```bash
youtube-api-tool jobs run --file jobs.csv --plan-out plan.json
```

2) Review the plan, then inspect the safe refusal path:

```bash
youtube-api-tool --apply --yes --ack-no-snapshot --plan-in plan.json jobs run --file jobs.csv
```

Note: when applying from `--plan-in`, this template requires the original `--file` so it can verify `job_file_sha256` and refuse if the job file changed since plan creation.

## CSV format

The CSV must include an `action` column.

This tool includes demo job actions:
- `read.ping` (safe; does not require `--apply`)
- `write.ping` (requires `--apply --yes`)

Example:

```csv
action
read.ping
```

If you include a write action, the tool returns a safety refusal instead of running a real YouTube write:

```bash
youtube-api-tool --apply --yes --ack-no-snapshot jobs run --file examples/jobs_with_write.csv
```
