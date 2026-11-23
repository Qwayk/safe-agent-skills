# Approve Awin order submissions

Start by checking the publisher account and advertiser program. Most commands read Awin data. Feed downloads save to the file you choose with `--out`. An enhanced feed replaces an existing file only when you allow overwriting and the download passes the file checks.

## Review the plan

The order command is the one command that sends a live change to Awin. Awin must enable the publisher, and the advertiser must enable the program for that publisher. [Awin’s requirements](https://help.awin.com/apidocs/proof-of-purchase-publisher-transaction-api)

Save the plan with `--plan-out`. Before approval, check the publisher ID, advertiser ID, order file, and how you’ll check for duplicate orders. Keep the plan and order data local. The plan records a fingerprint of the selected key without storing the key. The tool checks the key, account IDs, and order file again before sending. Save a new plan if you change the key or order file, or if the plan was saved before key checking was added.

## Submit and check the receipt

Run the approved action with `--apply --yes --plan-in`. Choose `--receipt-out` to keep the receipt. [Exact commands](command_reference.md#proof-of-purchase)

- `accepted_pending` means Awin accepted the submission. Check the pending orders in Awin before reporting them as verified.
- `provider_reported_errors` means Awin returned an error in the reply. Check which orders reached Awin before trying again.
- `outcome_unknown` means the reply did not confirm what happened. Check the orders in Awin before resending.

Awin’s docs give no way to undo an order submission through this API. Check what happened with the publisher or advertiser before making another change.
