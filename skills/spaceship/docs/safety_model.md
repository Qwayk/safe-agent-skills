# Review a Spaceship change

Check the account, domain, and exact request before approving it. Use the same credentials, settings folder, and request values when you apply with `--apply --yes --plan-in`. Make a new plan if your credentials changed or the plan uses the old format. A preview without credentials can help you prepare the request. Save and review a new plan with the intended account before you apply.

Each apply saves an attempt receipt under `.state/receipts/` beside your settings before sending the change. Keep it so the tool can stop a second attempt from the same plan. Use a new filename if you pass `--receipt-out`. Keep settings, plans, request bodies, and receipts in separate files.

## Review prices and transfers

For a registration, renewal, or transfer, check the domain, the term, and the currency. The tool shows the exact-domain price from Spaceship, checks it again before sending, and stops if it changes. If Spaceship does not return a usable price for the term, check and complete the purchase in Spaceship. The price is a quote. A promotion can run out before the provider charges you. [Spaceship pricing docs](https://docs.spaceship.dev/#tag/Domain-Pricing/operation/getSingleDomainPricing)

New transfers and SafePay deals can have no earlier record, or the key can have permission to send the request without permission to read that record. The plan shows what Spaceship returned and asks for `--ack-no-snapshot`. If the read result changes after review, save a fresh plan. Keep transfer codes, contact details, and payment information in private request files.

## Review a SafePay deal

Before approval, check the domain, amount, currency, fee split, how the purchase is paid, and the buyer or seller who will receive the invitation. If the broker is confirming a party's terms for them, review that choice too. Read the counterparty details from the private request file.

The receipt checks that the returned deal matches the reviewed domain and terms. It shows who still needs to confirm when Spaceship supplies that status. An active deal is waiting for purchase. [Spaceship SafePay docs](https://docs.spaceship.dev/#tag/SellerHub/operation/createSafePayTransaction)

## Read the receipt

A reply marked `accepted_not_completed` is still processing. Use its operation ID with `async-operations status`. If the reply was lost or the result is unclear, check Spaceship before making a new plan. The tool cannot undo a provider change for you.

The plan lists the required flags. Purchases need `--ack-spend`, ownership changes need `--ack-ownership`, and changes to DNS or nameservers need `--ack-dns-risk`. Checkout and SafePay ask for `--ack-financial`. Deletions and private data use `--ack-destructive` and `--ack-private-data` where applicable. See the [commands](command_reference.md) for the exact flags.

Run history defaults to `.state/runs/<run_id>/`. Choose a short local name for `--run-id`. Use `runs list` and `runs show` to find recent results. Run history keeps contact and transaction identifiers masked.
