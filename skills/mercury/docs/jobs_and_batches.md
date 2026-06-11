# Batches (exports/downloads)

This tool does not currently support “jobs from CSV” for Mercury API actions (it is read-only for API writes).
Instead, the batch-capable features are local exports and downloads.

```bash
mercury-api-tool export transactions --format csv --out transactions.csv
```

## Safety rules

- Without `--apply`, exports/downloads are dry-run and emit a plan (no files are written).
- Any local file write requires `--apply` to execute.
- Overwriting an existing output file requires `--yes`.
- Output is exactly one JSON object in `--output json` mode.

## Plan files (recommended for overwrite/batch)

For exports/downloads, prefer:

1) Create a plan file (dry-run):

```bash
mercury-api-tool export transactions --format csv --out transactions.csv --plan-out plan.json
```

2) Review the plan (human/Codex), then apply from the saved plan:

```bash
mercury-api-tool --apply --yes --plan-in plan.json export transactions --format csv --out transactions.csv
```
