# Jobs and batches

Batch operations are run from a CSV file:

```bash
zendesk-api-tool jobs run --file jobs.csv
```

## Safety rules

- Jobs are strict by default.
- Without `--apply`, jobs run in dry-run mode and include a plan for write rows.
- Any write action requires `--apply --yes`, then requires explicit no-snapshot approval before any Zendesk write while before-state support is missing.
- Plans and missing-approval refusals are plan-first and proof-first: review dry-run output and do not expect live writes yet.
- Recovery is explicit: no automatic rollback promise and no implied snapshot or backup, no implied restore.
- The runner stops on the first error and exits non-zero.
- Output is exactly one JSON summary object.

## Plan files (recommended for risky jobs)

If a jobs run includes writes, prefer:

1) Create a plan file (dry-run):

```bash
zendesk-api-tool jobs run --file jobs.csv --plan-out plan.json
```

2) Review the plan (human/Codex), then test the gate path if needed:

```bash
zendesk-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv
```

Note: when applying from `--plan-in`, the tool requires the original `--file` so it can verify `job_file_sha256` and refuse if the job file changed since plan creation.

The apply attempt requires explicit no-snapshot approval for write rows until per-row saved snapshot support is available.

If a restore action is available in the API command surface, run it later as a separate explicit command; no plan or receipt rollback is generated here.

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

If you want to include a write action, run without `--apply` for the plan. An Apply with `--apply --yes` also needs explicit no-snapshot approval when no saved snapshot is available:

```bash
zendesk-api-tool --apply --yes jobs run --file examples/jobs_with_write.csv
```
