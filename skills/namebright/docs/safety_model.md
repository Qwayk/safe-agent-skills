# Review a NameBright change

Start with a saved plan and check the account, domain, exact values, and any people the request will contact. To apply it, use the same credentials, settings folder, and values with `--apply --yes --plan-in`. Make a new plan if your credentials changed or the saved plan is from the old format.

Choose a new receipt file if you pass `--receipt-out`. The tool saves a private receipt for each attempt in `.state/receipts/` next to your settings. It uses that file to stop a second apply from the same plan, even if you use a different receipt name. If a reply is unclear, check the order or domain in NameBright before making a new plan. The tool has no automatic restore.

## Before a purchase

Review the exact domain, years, and price with `--ack-spend`. The plan shows the price returned by NameBright and an estimated total. For more than one year, it uses the standard yearly price to estimate the total. NameBright sets the final charge and draws it from your funded balance. Domain purchases are non-refundable.

The tool checks the quote again just before sending. If the price changes, make a new plan. If the API can't give a usable price, move to NameBright checkout to see the charge and decide there.

A purchase response can say that NameBright has taken payment and is still creating the order. Keep its order number. The tool checks that number once and shows a pending result if the order is still unavailable. Use `orders get --customer-order-number <number>` to check it later. Resending the purchase can charge you twice. [NameBright API docs](https://api.namebright.com/documentation/current/doc.json)

## Before an account move

Check the domain and the receiving NameBright account. An outbound request can notify the recipient. Get approval for the move and the notification using the flags listed by the plan. A pending request means the domain is still waiting to move. The tool checks the pending and completed lists for the domain and leaves the result unconfirmed if the list gives no evidence of the change.

The July API docs covered two force-move commands that can create a recipient account and send a temporary password. The current docs omit them. The old command names still exist with their ownership, account-creation, and message approvals.

## Contacts, DNS and receipts

Review the specific fields for contact, DNS, and settings changes. Contact plans use a private fingerprint of what you reviewed, and the tool checks the current contact before sending. Changes that remove records need the destructive-action approval in the plan.

Get approval for the exact destination before sending verification by email, SMS, or voice. Give verification codes to the tool through the required private file during apply. Keep credentials and codes out of chat, receipts, and logs.

Read the receipt for the provider reply and the separate result check. The `runs list` and `runs show` commands help you find recent receipts. If an expected change is unconfirmed, check NameBright before trying again.
