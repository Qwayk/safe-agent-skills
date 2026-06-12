# Jobs and batches

Use jobs when you want one repeatable check over many rows.

A CSV file is a simple spreadsheet-style file. Each row tells the tool which action to run.

```bash
qwayk-jobber-safe-agent-cli --output json jobs run --file jobs.csv
```

Job files use the same named operation surface as the CLI:

- `read.<JobberQuery>`, for example `read.clients`
- `write.<JobberMutation>`, for example `write.clientCreate`

## Safety behavior in jobs

- Without `--apply`, jobs only show a plan.
- Any write action in a job requires `--apply --yes` to execute.
- For plan-based replay, pass both `--plan-out` and `--plan-in`.
- Applying a jobs plan with `--apply --yes --plan-in` verifies the job file hash and refuses if the file changed.

## Command patterns

```bash
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json jobs run --file jobs.csv
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json jobs run --file jobs.csv
```

## Notes

- Batches in this tool are designed for repeatable safety workflows.
- For direct Jobber API edits, use direct `read` or `write` commands.
