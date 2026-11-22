# Wix approvals and receipts

First confirm the account or site. Use a named command from [Commands](command_reference.md). A preview can read Wix to save the current state. It stops before making the change.

1. Save the proposed change with `--plan-out`. Check the account or app connection, the target, the values, and what can be checked afterward.
2. Apply the approved plan with `--plan-in --apply --yes`. Use `--ack-irreversible` if the command requires it. If a result says `refused: true`, the tool stopped before applying the change.
3. Read the receipt. A request can be accepted while a check is still pending or unavailable. Use the named status or read command from the guide before trying again.

Products V3 and Site Actions compare the saved request and connection with the current one. Older plans for those commands need a new preview. If a manual or saved app token changed, make a new plan. App credentials use the app and installation they belong to, so a newly issued token from those same credentials does not invalidate the review.

A product update receipt checks the values Wix returns. A publish receipt reports whether Wix sees the site as live. Open the public page to check whether the intended content is visible, especially if the site was already live. [Wix publish docs](https://dev.wix.com/docs/api-reference/account-level/sites/site-actions/publish-site)

Use `--receipt-out` to choose where a receipt goes. `runs list` and `runs show` open local run records. Keep plans and receipts private when they contain account data. Where Wix cannot give a saved copy of the previous state or a reliable way to undo a change, show that limit during review.
