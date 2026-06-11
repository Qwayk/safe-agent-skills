# Bulk Jobs and Async Work

This tool ships only these Salesforce Bulk API 2.0 job families:

- `jobs-ingest`
- `jobs-query`

Full shipped actions:

- `jobs-ingest`: `list`, `create`, `get`, `upload`, `upload-complete`, `successful-results`, `failed-results`, `unprocessed`, `abort`, `delete`
- `jobs-query`: `list`, `create`, `get`, `results`, `result-pages`, `abort`, `delete`

## Ingest flow

1. Create the ingest job:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-ingest create --body-file ingest-job.json
```

2. Upload CSV rows:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-ingest upload --job-id 750... --data-file rows.csv
```

3. Mark upload complete:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-ingest upload-complete --job-id 750...
```

4. Read state or download results:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-ingest list
qwayk-salesforce-platform-safe-agent-cli jobs-ingest get --job-id 750...
qwayk-salesforce-platform-safe-agent-cli jobs-ingest successful-results --job-id 750... --download-to successful.csv
qwayk-salesforce-platform-safe-agent-cli jobs-ingest failed-results --job-id 750... --download-to failed.csv
qwayk-salesforce-platform-safe-agent-cli jobs-ingest unprocessed --job-id 750... --download-to unprocessed.csv
```

## Query flow

1. Create the query job:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-query create --body-file query-job.json
```

2. Poll state:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-query list
qwayk-salesforce-platform-safe-agent-cli jobs-query get --job-id 750...
```

3. Download CSV result pages:

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-query results --job-id 750... --download-to results.csv
qwayk-salesforce-platform-safe-agent-cli jobs-query result-pages --job-id 750...
```

## Safety flow for shipped jobs commands

- Write actions are dry-run by default and return a plan.
- `jobs-ingest create`, `upload`, `upload-complete`, `abort`, `delete`, and `jobs-query create`, `abort`, `delete`
  require `--apply --yes` before an apply request and may require `--ack-irreversible` when configured as irreversible.
- Current job write apply requests require explicit no-snapshot approval before Salesforce HTTP until the command can save real before-state when possible.
- Reads use `--job-id` and `--query-param` where needed with no extra write flags.
- Use `--download-to` for all CSV result outputs before post-processing.
