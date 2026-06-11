# Safety model

Rules:
- Dry-run by default.
- Live reads require `--live`.
- When no saved snapshot or provider backup is available, live Stripe API writes require explicit no-snapshot approval.
- Refuse when unsure; do not guess.
- Batch jobs require `--apply` and `--yes`.
- Never log secrets.
- No snapshot-based rollback is provided by the tool.

## Stripe-specific safety flags

- `--live`: executes HTTP requests to `https://api.stripe.com`. For API writes, it must be paired with the normal write gates and, when needed, `--ack-no-snapshot`.
- `--stripe-account <acct_...>`: targets a connected account via the `Stripe-Account` header.
  - If `STRIPE_ACCOUNT_ALLOWLIST` is set, values not in the allowlist are refused.
- `--idempotency-key <value>`: sets `Idempotency-Key` for write-like operations.
  - If omitted, the tool derives a deterministic key from the plan hash.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- For reads, the tool can make a live request when `--live` is present.
- For API writes, the tool discloses the recovery limit and requires explicit no-snapshot approval when no saved snapshot or provider backup exists.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply

Recommended workflow for Stripe API writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) If the plan still matches and you accept the recovery limit, apply with the required flags plus `--ack-no-snapshot`.

## Plans and API write approval path

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- why live API write apply requires explicit no-snapshot approval today when no saved snapshot is available

Without `--ack-no-snapshot`, a reviewed Stripe API write still refuses safely before Stripe HTTP. With the reviewed plan and explicit no-snapshot approval, supported API writes can run and emit an API receipt.

Plans and refusals must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: prove a saved plan still matches the attempted apply
- `--receipt-out <path>`: write the apply receipt JSON to a file

When no saved snapshot or provider backup is available, API write apply still requires explicit no-snapshot approval even when plan drift checks pass.

## Run history (recommended for customer-ready tools)

For write-capable commands, `stripe-api-tool` automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

It also appends a simple history row to:
- `.state/runs/index.jsonl`

These live next to your `--env-file` (usually next to your `.env` file), so you can always find them.

This is designed for vibe coders:
- You can ask your agent “what happened last time?” and it can use `runs list/show`.
- You don’t need to manually browse folders.

Rules:
- These artifacts must never include secrets.
- Plans, receipts, refusal summaries, and audit logs are proof of what was reviewed and what actually ran.

## Risk levels (Stripe)

This tool’s risk level is based on HTTP method + endpoint patterns and is enforced by the flags table below.

Examples:
- Low: `GET` (read-only).
- Medium: normal writes like creating/updating non-money-moving resources.
- High: money-moving writes (payments, payouts, transfers, refunds).
- Irreversible: `DELETE` operations.

## Risk tiers (enforced for `stripe-api-tool api ...`)

The tool uses a deterministic classifier based on HTTP method + endpoint patterns.

| Tier | Typical operations | Required flags before API write refusal |
|---|---|---|
| low | read-only methods (`GET`, `HEAD`, `OPTIONS`) | `--live` |
| medium | normal writes (`POST`/`PUT`/`PATCH`) not classified as money-moving | `--live --apply`, then `--ack-no-snapshot` when no saved snapshot or provider backup is available |
| high | money-moving writes (example: `payment_intents`, `charges`, `payouts`, `transfers`, `refunds`, invoice payment `POST /v1/invoices/{invoice}/pay`) | `--live --apply --yes --plan-in <plan.json> --ack-spend-money`, then `--ack-no-snapshot` when no saved snapshot or provider backup is available |
| irreversible | `DELETE` operations | `--live --apply --yes --plan-in <plan.json> --ack-irreversible`, then `--ack-no-snapshot` when no saved snapshot or provider backup is available |

Notes:
- High/irreversible tiers require `--plan-in` so “apply” is driven by the reviewed plan, not by ad-hoc flags.
- Classification is deterministic. Any write-like operation is gated at least as `medium` (requires `--live --apply`), and money-moving patterns are escalated to `high` (requires `--yes --plan-in --ack-spend-money`).
- After those gates pass, API writes still require explicit no-snapshot approval before HTTP when no saved snapshot or provider backup exists.

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Rollback (recommended default)

- The tool does not create snapshots and does not do automatic rollback.
- API write apply requires explicit no-snapshot approval when no operation-specific snapshot or provider backup is available.
- Recovery for any future supported write must be manual or via a follow-up plan that is explicitly reviewed.
