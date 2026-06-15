# Safety model

Zendesk can touch tickets, users, organizations, groups, macros, jobs, and support content, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the ticket or user first, keep sensitive support payloads private, and review the plan before any ticket or account change."

## Safe by default

- Offline plans are the default.
- No network calls happen unless you add `--live`.
- Read operations can run live with `--live`.
- The pinned Zendesk command inventory can be validated offline.
- Secrets are redacted from logs and artifacts.

## Sensitive-data rule

Zendesk outputs can include ticket bodies, names, emails, phone numbers, addresses, internal notes, and other support details.

That means:

- treat saved plans, receipts, and JSON output as sensitive
- avoid pasting raw Zendesk payloads into chat when you do not need them
- keep local artifacts private even for read-only work

## What slows down on purpose

- API writes start as dry-run plans first.
- When there is no saved before-state, API writes need explicit no-snapshot approval before Zendesk HTTP.
- Delete-style actions also need `--ack-irreversible`.
- Demo writes and some jobs write rows still refuse honestly instead of pretending to perform real Zendesk writes.

## What the approval flags mean

- `--live` means "run the real Zendesk read now."
- `--apply --yes` means "I reviewed the plan and want the write attempt to continue."
- `--ack-no-snapshot` means "I understand there may be no saved before-state to roll back from."
- `--ack-irreversible` means "I understand this delete or one-way action may not be reversible."

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- API apply paths can save receipts with `--receipt-out` when the command supports it.
- Safe refusals prove when nothing changed.
- Local run history stays under `.state/runs/`.
- Plans, refusals, receipts, and audit logs must stay secret-safe.

## Recovery limits

- Recovery is explicit only.
- Do not assume automatic rollback, backup, or snapshot support unless the plan says it exists.
- If a restore action exists for a Zendesk operation, it should run as a second explicit step, not as a silent rollback.

## The practical review loop

For anything risky, the expected flow is:

1. Generate the dry-run plan.
2. Review the records, payload, sensitive-data exposure, and permissions.
3. Approve the exact live flags only if the plan still looks right.
4. Check the receipt or refusal so you know what really happened.
