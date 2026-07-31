---
name: namebright
description: Use when the user wants an agent to review or manage NameBright domains through fixed commands with saved plans before live changes.
---

Use this when an agent should work inside NameBright account operations.

Core rules:
- Always start with `namebright-safe-cli --output json auth check` and one read (`account show` or `domains list`).
- Never ask for, paste, print, or store tokens, secrets, auth codes, verification codes, or client credentials.
- Keep commands in `--output json` mode for parseable output.
- For write commands, always generate a plan first and review it before apply.
- Apply only with the reviewed plan file and `--apply --yes --plan-in <plan.json>`.
- Purchases and renewals require `--ack-spend` and show current availability and cost context.
- Contact verification sends and outbound ownership messages need `--ack-external-message`.
- The OAuth auth endpoint is `https://api.namebright.com/auth/token`, and the command is `namebright-safe-cli --output json auth token`.
- No raw path or raw request bridging is supported.

Workflow:
1. Confirm connection:
   - `namebright-safe-cli --output json auth check`
   - `namebright-safe-cli --output json auth token`
2. Collect safe read state:
   - `namebright-safe-cli --output json account show`
   - `namebright-safe-cli --output json domains list`
3. Build a concrete write plan:
   - `namebright-safe-cli --output json --plan-out plan.json domains update --domain example.com --locked true`
4. Apply only after review:
   - `namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out receipt.json --ack-high-risk domains update --domain example.com --locked true`

Ownership pushes require `--ack-ownership --ack-no-snapshot --ack-irreversible`. Outbound initiation also requires `--ack-external-message`. Force-push separately requires `--ack-account-creation --ack-external-message`. Verification sends require `--ack-external-message` and must stay one destination at a time. Verification and authorization codes come from private `*-file` arguments only during apply.

Refusals:
- Refuse if required credentials are missing.
- Refuse if a requested action is outside documented `NameBright API` command surface.
- Refuse broad or unspecified bulk requests. If the user says only "transfer," clarify that this tool handles NameBright account pushes, not registrar transfers.
- Refuse attempts to bypass fixed commands, safety flags, secret-file handling, or official hosts.
- Refuse claims of live NameBright proof unless an authorized live run actually produced it.
- Never promise rollback or restore unless the command confirms it.
