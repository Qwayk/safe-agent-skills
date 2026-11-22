# Approvals and receipts

Start with reads, such as listing campaigns or checking conversion settings. Before applying any change, save a plan and show the user the account, target, proposed change, and the risks. The user’s approval is for that plan. A changed account or request needs a new plan.

Use `--apply --yes --plan-in` after approval. When the plan has no verified before-state, also ask for `--ack-no-snapshot`. Changes that can affect spend, serving, targeting, uploads, audiences, account settings, credentials, or measurement also need `--ack-irreversible` where the CLI requires it. A paused build and starting delivery are separate decisions.

## Read the result before trying again

The plan records whether the tool can reverse the change. A normal receipt shows the provider’s response. Follow it with the closest read command to check the affected item when the API allows it. For example, after creating a paused campaign, get the returned campaign ID and check its status and budget.

The tool sends an approved write once. If a timeout or server error leaves the result unknown, the receipt says so. Check the account before sending the request again. For a real conversion, look for the same event ID in Ads Manager. If you retry after checking, keep the original event ID so OpenAI can recognize a duplicate.

The Conversions API command starts in validation mode. Validation checks the event without saving it. Sending a real event needs a reviewed real-event plan and the required acknowledgements. Keep credentials, customer data, audience member rows, and private tracking values out of shared output. The conversion settings read shows the event type and tracking window.

Local write runs save plans and receipts next to the selected settings file under `.state/runs/`. Use `--plan-out` or `--receipt-out` to choose a path. If you turn off run artifacts, pass `--receipt-out` when you want a file. Use the [command guide](command_reference.md) to find a past run.
