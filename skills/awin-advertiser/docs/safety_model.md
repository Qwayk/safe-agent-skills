# Review changes before sending them

Ask for a preview before approving transaction changes, an offer, a feed upload or a conversion order. The preview sends no write request to Awin. Save it with `--plan-out`.

## What to check in the plan

- Confirm the advertiser ID, the proposed action, and the exact file the agent will send. For example, check the transaction IDs and changed amounts in a validation batch, or the product count and locale of a feed.
- Confirm the webhook destination if Awin will send order updates there. Ask where to check the result and what you can do if the change needs correcting.
- Send the change only after you approve it. Apply uses `--apply --yes --ack-irreversible --plan-in`. The tool compares the saved plan with the current account, URL, token and contents of the input file. It also checks the feed locale or conversion webhook where applicable. Make a new plan after a change, and for plans saved before the November 23 approval update.

## What to check in the receipt

Compare the account and action with your plan. The receipt shows what Awin confirmed, what is still pending and what could only partly finish. The agent should give you the receipt path and tell you what to check next. You can use `--receipt-out` to choose that path.

A pending or missing reply can mean Awin received the request. Check the account, transaction job, feed version or order webhook before trying again. For a partly successful order batch, check the failed order references and leave successful orders out of any new plan. If a completed change needs correcting, check what Awin allows for that action and review the correction separately.

Keep tokens, customer data and private file contents out of shared messages. [Exact commands](command_reference.md)
