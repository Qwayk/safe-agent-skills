# Jobs and batches

Batch operations are run from a CSV file:

```bash
stripe-api-tool jobs run --file examples/jobs.csv
```

## Safety rules

- Jobs are strict by default.
- Without `--apply`, jobs run in dry-run mode and include a plan for write rows.
- Any write action requires `--apply --yes` to actually execute.
- The runner stops on the first error and exits non-zero.
- Output is exactly one JSON summary object.

## Plan files (recommended for risky jobs)

If a jobs run includes writes, prefer:

1) Create a plan file (dry-run):

```bash
stripe-api-tool jobs run --file examples/jobs.csv --plan-out plan.json
```

2) Review the plan (human/Codex), then apply from the saved plan:

```bash
stripe-api-tool --apply --yes --plan-in plan.json jobs run --file examples/jobs.csv
```

Note: when applying from `--plan-in`, this tool requires the original `--file` so it can verify `job_file_sha256` and refuse if the job file changed since plan creation.

## CSV format

The CSV must include an `action` column.

This tool includes demo actions:
- `read.ping` (safe; does not require `--apply`)
- `write.ping` (requires `--apply --yes`)

Example:

```csv
action
read.ping
```

If you want to include a write action, run with `--apply --yes`:

```bash
stripe-api-tool --apply --yes jobs run --file examples/jobs_with_write.csv
```
