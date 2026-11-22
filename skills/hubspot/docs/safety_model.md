# Review a HubSpot change

Start with a read so you can confirm the account and records. A write command previews the request unless you pass `--apply`.

## Before you send a change

1. Run the command without `--apply`. Use `--plan-out plan.json` to save the preview at a known path.
2. Review the records, fields, filters, and files. Check that the connection is for the intended account. Ask what you can recover in HubSpot if something goes wrong.
3. After the user approves, add `--apply` and `--ack-no-snapshot`. The tool has no saved copy of the old data, provider backup, or automatic undo. Add `--yes` and `--ack-irreversible` where the [command list](api_coverage.md) calls for them.
4. Pass the saved plan with `--plan-in plan.json` for imports, bulk changes, GDPR deletion, and custom schema hard deletion. If you pass a saved plan for another write, the same checks apply. The URL, command, request, upload names and contents must match, and the same token must be in use.

You can preview offline without a token. To use that preview for a live change, first make a fresh one with the right connection. Also make a new preview if you have an old plan or changed the token or request. The tool compares the connection locally without adding a HubSpot permission or storing the token in the plan.

## After you send a change

Read the receipt to see what HubSpot reported. For an import, use the printed commands to check its progress and errors. A job that HubSpot accepted can still be running. For a bulk change with errors, check which records succeeded before deciding what to do with the failed records. Check the affected records in HubSpot if you need to verify the outcome. If the tool refused, its message says what you need to fix before trying again.

## Where the records go

By default, the tool keeps previews, receipts, summaries, and audit logs under `.state/runs/<run-id>/` next to your settings file. Use `runs list` or `runs show --run-id <id>` to find them. A refused write has a summary and reason. Receipts record replies to requests that were sent. Keep these files private because they can contain customer data.
