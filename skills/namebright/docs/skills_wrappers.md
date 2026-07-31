# Skills wrappers

This page documents how the agent-facing wrapper should present this tool.

## What the wrapper should tell the agent

- Use this skill only for NameBright operations in this tool.
- Start with `namebright-safe-cli --output json auth check`, then `namebright-safe-cli --output json account show` or `namebright-safe-cli --output json domains list`.
- Never ask for, print, or store tokens, auth codes, verification codes, or client credentials.
- Keep output parseable with `--output json`.
- Write commands are plan-first. Do not apply directly.
- Apply only with reviewed plan file: `--apply --yes --plan-in <plan.json>`.
- Purchases and renewals require `--ack-spend`.
- NameBright account pushes and external-message flows require explicit additional acknowledgements.
- No raw request or raw path bridging is supported.

## Runtime specifics

- Fixed endpoint families:
  - Domain API base: `https://api.namebright.com/rest`
  - OAuth endpoint: `https://api.namebright.com/auth/token`
- Write path requires write flags:
  - `--plan-out <path>` (save plan)
  - `--plan-in <path>` (apply from reviewed plan)
  - `--receipt-out <path>` (save receipt, required when artifacts are off)

## First safe workflow

1) Confirm connection:
   - `namebright-safe-cli --output json auth check`
2) Collect read state:
   - `namebright-safe-cli --output json account show`
   - `namebright-safe-cli --output json domains list`
3) Build a concrete plan:
   - `namebright-safe-cli --output json --plan-out plan.json domains update --domain example.com --locked true`
4) Apply only after review:
   - `namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out receipt.json --ack-high-risk domains update --domain example.com --locked true`

Ownership pushes additionally require `--ack-ownership --ack-no-snapshot --ack-irreversible`. Outbound initiation also sends an outside message, so it requires `--ack-external-message`. Force-push separately requires both `--ack-account-creation` and `--ack-external-message`.

Verification sends are outside messages and must be one destination at a time. Code-verification commands read the code from the command's private `*-file` argument only during apply. Refuse any request to reveal, save, or bypass those values, to invent a raw request, or to claim live proof that was not actually run.
