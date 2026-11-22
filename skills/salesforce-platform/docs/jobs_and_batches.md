# Import and export jobs

Salesforce processes Bulk API 2.0 jobs in the background. A job ID lets you check what has run and which rows need attention.

## Import a CSV

Use these commands in order. Finish and check each step before previewing the next one.

1. Preview the job and review the object and operation.

   ```bash
   qwayk-salesforce-platform-safe-agent-cli --plan-out create.json jobs-ingest create --body-file ingest-job.json
   ```

2. After creating the approved job, use the job ID from its receipt to preview the upload.

   ```bash
   qwayk-salesforce-platform-safe-agent-cli --plan-out upload.json jobs-ingest upload --job-id 750... --data-file rows.csv
   ```

3. After uploading, preview the step that tells Salesforce to start processing. The tool reads the job to confirm its operation before showing you the plan.

   ```bash
   qwayk-salesforce-platform-safe-agent-cli --plan-out start.json jobs-ingest upload-complete --job-id 750...
   ```

For each approved step, use the same command with `--apply --yes --ack-no-snapshot --plan-in <file>` before `jobs-ingest`, and omit `--plan-out`. Get explicit approval before creating or starting a permanent delete and include `--ack-irreversible`. The tool checks the job type again before it starts processing, including jobs created elsewhere.

## Check what happened

Run the status command before reporting an import as done. Salesforce can finish a job with some rows failed. Get the failed and unprocessed rows before deciding what to retry.

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-ingest get --job-id 750...
qwayk-salesforce-platform-safe-agent-cli jobs-ingest successful-results --job-id 750... --download-to successful.csv
qwayk-salesforce-platform-safe-agent-cli jobs-ingest failed-results --job-id 750... --download-to failed.csv
qwayk-salesforce-platform-safe-agent-cli jobs-ingest unprocessed --job-id 750... --download-to unprocessed.csv
```

## Export with a query job

Preview the query first. Start the approved job using the [approval steps](safety_model.md), then check its status and download the finished results.

```bash
qwayk-salesforce-platform-safe-agent-cli jobs-query create --body-file query-job.json
qwayk-salesforce-platform-safe-agent-cli jobs-query get --job-id 750...
qwayk-salesforce-platform-safe-agent-cli jobs-query results --job-id 750... --download-to results.csv
qwayk-salesforce-platform-safe-agent-cli jobs-query result-pages --job-id 750...
```

Both job types have `list`, `abort`, and `delete` actions. Abort and delete are changes. Follow the approval flags for those commands. [Salesforce job states](https://developer.salesforce.com/docs/platform/api-asynch/guide/bulk-api-2-job-states.html)
