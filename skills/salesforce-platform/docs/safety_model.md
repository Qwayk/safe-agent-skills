# Review a Salesforce change

Start with a read to confirm the org, object, and records. Write commands run as previews by default. A few requests use POST to produce a read result, such as parameterized search, scheduling lookups, or generating an OpenAPI description.

## Before sending a change

1. Preview the change without `--apply`. Use `--plan-out plan.json` to save the preview. Review the records, fields, request options, and files. For blob uploads, the preview lists the parts and a check for their contents.
2. Review the recovery limit. This tool does not save a copy of the old data or undo changes. Get approval for the change and for proceeding without a saved copy.
3. Send an approved change with `--apply --ack-no-snapshot` and any flags the command needs. Bulk and other higher-risk actions also need `--yes`. Some deletes and resets need `--ack-irreversible`.
4. Pass `--plan-in plan.json` for Composite writes, Bulk API ingest changes, and password changes. Whenever a saved plan is used, the tool checks the connection, request path, options, and inputs before sending the change. Make a fresh plan if a token or request changed, or if the plan came from an older version of the tool.

## Starting a bulk import

When you preview or apply `jobs-ingest upload-complete`, the tool reads the job to confirm what it will do. It stops if Salesforce reports a different job type from the one in the plan. Permanent bulk deletes require `--ack-irreversible` when creating the job and when starting it. This also applies when the job was created elsewhere. [Full bulk workflow](jobs_and_batches.md)

## Check the receipt

Read `verification.outcome` in the receipt. A submitted job has been accepted and may still be waiting or running. Use the job ID to check its current state and read its failed or unprocessed rows. A grouped request can report failures even when its HTTP response indicates success. Check the individual results before considering a retry.

If the tool refuses, read the reason and review a fresh plan or get the missing approval. Check the live records if you need to confirm an outcome that the provider reply did not establish.

By default, previews, receipts, summaries, and audit logs are saved under `.state/runs/<run-id>/` next to the settings file. Use `runs list` and `runs show` to find them. Keep those files private if they contain record data.
