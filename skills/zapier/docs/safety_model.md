# Plans, approvals, and receipts

Start with a read to check the account and the item you want to change. Commands that send changes produce a plan by default. A stored plan is a record of what you reviewed.

## Before making a change

1. Check the account, command, target, and request body together. The plan stores a hash of the body, so read the original body you want to send.
2. Check what happens if the change runs and whether Zapier provides a way to undo it. Acknowledging an inbox message can remove it permanently. Save a separate copy of the previous state when you can.
3. After the person approves the change, run the same request with `--apply`, `--plan-in`, and the acknowledgement that fits. The CLI accepts `--yes`, `--ack-irreversible`, or `--ack-no-snapshot`. Use the last one when the approval is to proceed without a saved copy of the previous state.

The CLI compares the saved API address, operation, path, inputs, risk, and credentials with the current request. If something changed, review a fresh plan. If the result contains `refused=true`, it stopped before sending the change. Read `reasons` even if `ok=true`.

## After Zapier replies

Open the receipt to see what the request sent and what Zapier returned. A successful response code records Zapier’s reply. When the task depends on the changed state, use the matching read command to check the actual result.

For `partner create-action-run`, an accepted receipt means Zapier has taken the request. Open the result with the `verification.next_command` and the saved run ID. If Zapier supplied no ID or the reply was lost, check Zapier before running the action again. [How Zapier reports action results](https://docs.zapier.com/powered-by-zapier/running-actions/retrieve-action-run)

Use `runs list` and `runs show --run-id <id>` to find local records. Keep private input values and credentials in your local files.
