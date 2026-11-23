# Review a domain add

A stats request reads traffic and earnings from GiantPanda. Treat the results as private account data. Preparing a domain add saves a plan on your machine.

## Before sending

Review the exact domain names with the person who can approve the add. Keep the saved plan and its ID. Run the [apply command](command_reference.md#add-domains) with the same domains, token, and settings folder. If the token changed or the plan was prepared without one, make a fresh plan and ask for approval again. The same applies to plans saved before the November update.

GiantPanda has no documented way for this tool to save and restore the account’s earlier state. The approval command requires `--ack-no-snapshot` so this limit is clear before sending.

## After sending

The tool saves a private receipt before it sends the add. It records the result in `.state/receipts/` next to the settings file. One approval can send once from that settings folder. `--receipt-out` saves a second copy for you if needed.

- `created` lists the domains GiantPanda said it added.
- `existing` lists the domains GiantPanda said were already in the account.
- `needs_check` lists the domains the tool could not confirm. A lost reply can leave every domain in this list.

A receipt marked `pending` means the tool was interrupted before saving a final result. Open the GiantPanda dashboard and check the names before preparing another plan. For a confirmed rejection, fix the reason first. Ask for fresh approval for any names that still need to be added.

The [plan example](examples/plan.example.json) and [receipt example](examples/receipt.example.json) use made-up domains.
