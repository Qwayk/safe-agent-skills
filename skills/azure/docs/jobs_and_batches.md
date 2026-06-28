# Jobs and batches

Use jobs for repeatable work with a CSV file. A CSV file is a simple spreadsheet-style file.

## CSV format

- File must include an `action` column.
- Demo actions supported in current runner:
  - `read.ping`
  - `write.ping`

## Safety behavior

- Job runs are dry-run by default.
- Write actions in jobs are refused in apply mode.
- Use generated Azure service commands for real writes; those commands require a saved plan plus `--apply --yes`.
- Jobs can still save a local plan for review:

```bash
qwayk-azure-safe-agent-cli jobs run --file jobs.csv --plan-out plan.json
```

The runner tracks baseline and refuses if environment or source file checks fail.

## Read mode

```bash
qwayk-azure-safe-agent-cli jobs run --file jobs.csv
```

This returns planned output and does not apply changes.
