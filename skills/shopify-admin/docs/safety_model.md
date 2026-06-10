# Safety model

Rules:
- Dry-run by default; Shopify mutations start as plans.
- When no operation-specific saved snapshot is available, live mutation apply needs explicit no-snapshot approval.
- Refuse when unsure; do not guess.
- Never log secrets.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- After a write, the tool verifies the API state.
- When verification is not possible, the tool should label it as best-effort and explain.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) If you approve the recovery limit, apply with the required risk flags plus `--ack-no-snapshot`.

## Plans and apply refusals

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- why live apply requires explicit no-snapshot approval today
- how the tool will record the provider response after apply

Without `--ack-no-snapshot`, a reviewed mutation still refuses safely before Shopify HTTP. With the reviewed plan and explicit no-snapshot approval, the mutation can run and record a receipt.

Plans must never include secrets.

## Outputs and redaction rules (important)

This tool does **not** promise that stdout is redacted.

- **Stdout JSON (queries and plans):** not redacted. Treat it as sensitive, especially when using `--return-shape-file` because custom return shapes can include PII (personally identifiable information) like names, emails, addresses, phone numbers, and customer/order details.
- **Plan/audit artifacts:** best-effort redacted by key name, recursively. Common redaction keys include `authorization`, `token`, `access_token`, `secret`, `api_key`, `email`, `phone`, `name`, and address-like fields (`address`, `city`, `zip`, `postal`, `country`, `province`, `state`).
- **Redaction is not a guarantee:** keys can be unexpected, nested, or renamed. Always handle outputs/artifacts as sensitive data and avoid pasting them into chat or committing them to git.
- **Run artifacts live under `.state/` (gitignored):** keep your `.env` and `.state/` private.
- **Disabling artifacts:** `--no-artifacts` stops writing local plan/receipt/audit files, but stdout output is still printed.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: prove a saved plan still matches the attempted apply
- `--receipt-out <path>`: write the apply receipt JSON to a file

When no saved snapshot is available, apply still requires explicit no-snapshot approval even when plan drift checks pass.

## Run history (recommended for customer-ready tools)

For write-capable commands, this template automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

It also appends a simple history row to:
- `.state/runs/index.jsonl`

These live next to your `--env-file` (usually next to your `.env` file), so you can always find them.

This is designed for vibe coders:
- You can ask your agent “what happened last time?” and it can use `runs list/show`.
- You don’t need to manually browse folders.

Rules:
- These artifacts must never include secrets.
- Plans, receipts, and refusal summaries are proof of what was reviewed and what actually ran.

## Risk levels (guideline)

- Low: create new drafts; small safe edits.
- Medium: edit an existing draft; single-resource updates.
- High: edit published content; status changes; deletes; batch.
- Irreversible: actions that cannot realistically be undone (example: analytics events, licensing downloads).

High/irreversible actions should require an explicit plan + confirmation.

For irreversible actions, consider an extra acknowledgement flag:
- `--ack-irreversible`

## Shopify mutation risk gates (this tool)

The tool classifies mutation risk deterministically from the mutation name and enforces these minimum gates:

| Risk level | When it applies (name markers) | Required flags |
|---|---|---|
| `normal` | default | `--apply` |
| `high` | `Bulk`, `Batch`, `Import`, `Export`, `Publish`, `Subscription`, `Purchase`, `UsageRecord`, `Charge`, `Refund`, `Fulfillment`, … | `--apply --yes --plan-in` |
| `irreversible` | `Delete`, `Destroy`, `Remove`, `Purge`, `Uninstall`, `Cancel`, `Close`, `Deactivate`, `Revoke`, … | `--apply --yes --plan-in --ack-irreversible` |

Notes:
- The generated plan includes `risk_level` and `required_flags` so reviewers can see exactly what gates apply.
- When no operation-specific saved snapshot is available, live mutation apply also requires `--ack-no-snapshot`.

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Rollback (recommended default)

- Do not auto-rollback silently.
- This tool does not support automatic rollback or restore.
- If verification fails, stop and review before any follow-up action.
- If rollback is not possible in practice, label the action as irreversible in the plan/receipt.
- For actions that need a reverse path, include a manual recovery note that points to store-side options.
