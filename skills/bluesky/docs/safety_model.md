# Review and check Bluesky changes

API commands show a preview by default. Use `--live` for an actual read. Before a change, show the user which server, account, operation and data you will send and what can be recovered. Ask for approval of that change.

Use `--live --apply` to send an approved change. The preview lists any extra flags, including `--yes` for risky writes and `--ack-irreversible` for irreversible writes. API writes without a reliable copy of the previous state require `--ack-no-snapshot`. The receipt records that approval. There is no general restore command.

When a repository command creates or updates a Bluesky post, save the preview with `--plan-out` and use the reviewed file with `--plan-in`. Review the full request if it changes more than one record. The command checks the request and confirms the account with the planned server before it sends the write. If a field, account or server changes, make a new preview and get it approved. [Post example](quickstart.md#publish-a-post)

Use `--receipt-out` to save the response. Check for a refusal before claiming anything changed. For posts, read back the record and compare its text and content ID with the plan and receipt. The receipt records the API response and leaves automatic verification marked as skipped. If a response is lost, check the account before you send the change again. Use `runs list` and `runs show` to see local run records.

Keep settings, tokens and sensitive account details private.
