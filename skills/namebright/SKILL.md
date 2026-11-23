---
name: namebright
description: Check NameBright domains, DNS, renewals, and account moves. Prepare domain changes or purchases for approval.
---

# NameBright

Use `namebright-safe-cli` for the [named commands](docs/command_reference.md). Start with `auth check` and a read that answers the request, such as `domains list`. Use the intended account and settings file. For setup, see [Connect your NameBright account](docs/onboarding.md).

Use `--output json` and keep credentials, tokens, and verification codes out of chat. For a change:

1. Save a private plan. Show the account, domain, exact change, and any price or outside message before asking for approval. Confirm the receiving account for a move between NameBright accounts.
2. After approval, use the same settings and values with `--apply --yes --plan-in` and the plan's approval flags. Use private code files only during apply. Choose a new receipt filename if you supply one.
3. Read the receipt. Use the order number to check a paid order that's still pending. Check the account when the result is unclear or the expected change is unconfirmed. Make a new plan only after checking the prior result.

See [Review a NameBright change](docs/safety_model.md) for purchase, account-move, and message approvals. For a transfer to another registrar, use NameBright's registrar transfer process.
