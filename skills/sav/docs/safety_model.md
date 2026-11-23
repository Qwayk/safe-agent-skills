# Review SAV changes and receipts

SAV's API uses GET for all 12 commands. Four read data. The other eight can change the account and always start with a private plan.

## Before you apply

Check the intended account, domain, and requested values. A preview without an account key is useful for planning. Before applying, save and review a plan with the intended SAV key. If the key changed or the plan was saved before account checks were added, make a new plan.

To apply, use the same key and inputs plus `--plan-in`, `--apply`, `--yes`, `--ack-no-snapshot`, and `--ack-high-risk`. The existing approvals cover the risks of changing settings without a saved copy of the current state. The tool has no automatic restore for these changes.

The tool signs plans locally with the key in `.state/keys/plan-hmac.key` and checks them before sending a request. Choose separate paths for the settings file, plan, receipt, and any transfer-code file. If you use `--receipt-out`, choose a new file. The tool also keeps the receipt under the plan's own ID in `.state/receipts/`. That file records the attempt even when you chose another receipt path. Keep it so the tool can stop repeat attempts.

## Read the result

- A readable 2xx response is recorded as `provider_accepted`. To confirm what changed, check the account in SAV.
- A server error, lost connection, or unreadable 2xx reply leaves the result `unknown`. Check the current state in SAV before making a new plan. The CLI stops a second attempt from the same plan.
- If the tool cannot save the starting receipt, it stops before the request. If it cannot save the final receipt, the output still shows the response information it has. Check SAV before starting over.

`receipt_written` tells you whether the receipt was saved. `provider_response_received` tells you whether SAV replied. `durable_state_verified` is false because the tool cannot independently confirm the change.

The private plan has the exact values needed for apply. Displayed plans and receipts hide transfer codes and contact details. The CLI also removes known keys and transfer codes if SAV repeats them in a reply. It sends the key in the `APIKEY` header only to SAV's fixed API address and stops on redirects.
