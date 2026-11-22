# How approvals work

Run a preview first. GET and HEAD operations need `--live` to make an X call. Writes need `--apply --yes` after review. If the tool could not save the earlier state, use `--ack-no-snapshot` only after approving that limit. Deletes also need `--ack-irreversible`. Most writes have no automatic undo.

## What to review

Check that the plan shows the right account, target and exact change. Before posting, replying, deleting a post or sending a message, save a preview with `--live --plan-out`. X may charge for the checks done during preview, apply and post read-back. Apply with `--plan-in`. If the request or account changes, save and review a new plan.

A single direct message and a batch follow the same rules. Check that every recipient asked for or agreed to the specific message, and keep the evidence in the plan. Seeing that someone accepts DMs does not establish that they agreed to this one. Include a clear opt-out line, respect the opt-out list and stop messaging anyone who opts out. Use `dm send` or `dm bulk-send` to send one-to-one messages. The API message commands are available for previews, including group messages. [X automation rules](https://help.x.com/en/rules-and-policies/x-automation)

## Check what happened

A refusal reports `refused: true` in JSON and can exit with code 0. Check the output before moving on. After a create, the tool asks X for the post and checks that its ID and author match. A message receipt records acceptance only when X returns a message event ID. That cannot tell you whether the recipient read it. A batch stops at the first rejected or unconfirmed send and keeps the results it already got.

If X did not confirm a write, check X before trying again. Use the receipt to see where a batch stopped. Keep plans and receipts private. They can contain message text and the reason someone was contacted, even when tokens have been removed.
