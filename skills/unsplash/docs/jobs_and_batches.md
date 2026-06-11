# Jobs and batches

Batch operations are run from a CSV file:

```bash
unsplash-api-tool jobs run --file jobs.csv
```

## Safety rules

- Jobs are strict by default.
- Without `--apply`, jobs run in dry-run mode and include a plan for write rows.
- Any write action requires `--apply --yes`; when no saved snapshot is available it also requires explicit no-snapshot approval.
- The runner stops on the first error and exits non-zero.
- Output is exactly one JSON summary object.

## Plan files (recommended for risky jobs)

If a jobs run includes writes, prefer:

1) Create a plan file (dry-run):

```bash
unsplash-api-tool jobs run --file jobs.csv --plan-out plan.json
```

2) Review the plan (human/Codex), then try apply from the saved plan:

```bash
unsplash-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv
```

Note: when applying from `--plan-in`, this template requires the original `--file` so it can verify `job_file_sha256` and refuse if the job file changed since plan creation.

## CSV format

The CSV must include an `action` column.

This template includes demo actions:
- `read.ping` (safe; does not require `--apply`)
- `write.ping` (requires `--apply --yes`)

Example:

```csv
action
read.ping
```

If you want to include a write action, run with `--apply --yes`. Without explicit no-snapshot approval, apply refuses before execution. Approved applies must emit receipts that record the no-snapshot limit:

```bash
unsplash-api-tool --apply --yes jobs run --file examples/jobs_with_write.csv
```
