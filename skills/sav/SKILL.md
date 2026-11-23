---
name: sav
description: Check SAV domains, sales, and prices, or prepare a domain or listing change for approval.
---

# SAV

Use `sav` to check active domains, recent sales, and prices or prepare a change. Use the [named commands](docs/command_reference.md). Start with the account and domain the user asked about. Follow [account setup](docs/onboarding.md) when the key or settings file is missing.

Start with a read such as `sav domains active` or `sav pricing list` when it answers the request. The tool covers the 12 commands listed in the guide. For domain registration, auction bids, browser automation, or other API requests, use a different tool.

Use `--output json` unless the user asks for another format. Keep API keys, transfer codes, and contact details out of chat.

1. Save a private plan with `--plan-out` or use the default location. A preview can be made without a key. Before asking for approval, make a plan with the intended SAV key.
2. Show the user the account, domain, and exact change. Explain that the tool has no saved copy of the current state or automatic restore. For a transfer, read the code from a private `--auth-code-file` when making the plan, then remove the temporary file.
3. After approval, use the same account and inputs with `--apply --yes --plan-in --ack-no-snapshot --ack-high-risk`. Apply uses the saved transfer code from the plan.
4. Read the receipt. `provider_accepted` means SAV returned a readable success reply. To confirm the change, check the account in SAV. If the result is unclear or the final receipt could not be saved, check SAV before making a new plan.

See [approvals and receipts](docs/safety_model.md) for the full flow.
