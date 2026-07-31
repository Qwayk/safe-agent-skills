# Safety model

This tool is safe-by-default for reads and review-first for writes.

## Default behavior

- Read commands run without changing account state.
- Write commands are built as plans first.
- Live apply requires `--apply --yes --plan-in <plan.json>`.
- Required ack flags must match command risk and side effects.
- Secrets are never logged in plain output.

## What needs extra friction

- Purchases and renewals need `--ack-spend`.
- Domain settings, contacts, nameservers, DNS, and verification changes need `--ack-high-risk`.
- Ownership moves need `--ack-ownership`, `--ack-no-snapshot`, and `--ack-irreversible`.
- Inbound and outbound NameBright account-push actions are reviewed before any apply.
- Force-push also needs `--ack-account-creation` and `--ack-external-message` because it may create a recipient account and send a temporary password.
- Email, SMS, and voice verification sends need `--ack-external-message` and cannot run in bulk.
- Verification code actions are treated as high-risk input flows.

## Purchase and verification safety

- Register and renew requests must always be reviewed with exact domain and duration.
- Registration and renewal plans read availability, price information when NameBright returns it, and the account balance. Apply repeats those reads and refuses status or quoted-price drift.
- NameBright charges the funded account balance, and purchases are non-refundable.
- Verification send actions are treated as external customer messages.
- Code verification flows must not print code values.
- Verification and domain authorization codes are read from private files only during apply. Their values and file paths do not enter plans, receipts, logs, or summaries.
- Contact plans keep only redacted contact details plus SHA-256 digests that bind the requested values and complete provider snapshot. Apply compares a fresh raw snapshot digest in memory before any write.

## Recovery and rollback expectations

- Do not promise automatic rollback.
- The plan should clearly state when no restore snapshot is available.
- If the source does not expose reliable recovery, do not claim undo support.

## Run records

Write runs keep a local artifact record under `.state/runs/` for review.
This is for traceability only and does not expose tokens or auth values.
