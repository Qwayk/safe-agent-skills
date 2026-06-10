# Jobs and batches

Batch operations are run from a CSV file:

```bash
openai-api-tool jobs run --file jobs.csv
```

## Safety rules

- Jobs are strict by default.
- Without `--apply`, jobs run in dry-run mode and include a plan for write rows.
- Any write action still requires `--apply --yes`, but write rows require explicit no-snapshot approval when no saved snapshot is available; missing approval refuses before execution.
- The runner stops on the first error and exits non-zero.
- Output is exactly one JSON summary object.

## Plan files (recommended for risky jobs)

If a jobs run includes writes, prefer:

1) Create a plan file (dry-run):

```bash
openai-api-tool jobs run --file jobs.csv --plan-out plan.json
```

2) Review the plan (human/Codex), then attempt apply from the saved plan:

```bash
openai-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv
```

Note: when applying from `--plan-in`, this template requires the original `--file` so it can verify `job_file_sha256` and refuse if the job file changed since plan creation. If the job includes write rows, the approved apply records explicit no-snapshot approval and recovery limits and a refusal file when approval is missing.

## CSV format

The CSV must include an `action` column.

This template includes demo actions:
- `read.ping` (safe; does not require `--apply`)
- `write.ping` (plans only; apply attempts require `--apply --yes` and then require explicit no-snapshot approval before execution)

Example:

```csv
action
read.ping
```

If you want to include a write action, first create and review a plan. An apply attempt currently refuses safely:

```bash
openai-api-tool --apply --yes jobs run --file examples/jobs_with_write.csv
```
