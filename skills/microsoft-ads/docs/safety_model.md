# Safety model

Microsoft Ads can touch accounts, campaigns, budgets, ads, keywords, audiences, and reports, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the account or campaign first, then review the plan before budget, targeting, ad, keyword, or batch changes."

## Core safety rules

- No network without `--live`.
- Dry-run by default; no writes are sent while before-state capture is unsupported.
- Writes require explicit no-snapshot approval while before-state capture is unsupported; missing approval refuses before SOAP HTTP.
- Refuse when unsure; do not guess.
- Batch jobs require `--apply` and `--yes`.
- Never log secrets.

## How to review risky work

There are two kinds of safety:

1. What the tool checks
- Write plans include `before_state.required: true` and `before_state.supported: false`.
- Apply attempts for writes require explicit no-snapshot approval before SOAP HTTP or stub receipt output.

2. What a reviewer checks
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool can check gates and outputs, but a person or reviewing agent still needs to check whether the change is the right change.

## Plan → Review → Refusal

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) If apply is attempted, expect an explicit no-snapshot approval.
4) Use the plan, refusal, run summary, and audit log as proof that no Microsoft Ads write was sent.

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen

Approved apply attempts require explicit no-snapshot approval:
- why the write was blocked
- confirmation that no Microsoft Ads write was sent
- local run proof paths when artifacts are enabled

Plans, refusals, and any future receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: reserved for receipts from approved live writes; write applies require explicit no-snapshot approval before receipt output

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For write-capable commands, this template automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

It also appends a simple history row to:
- `.state/runs/index.jsonl`

These live next to your `--env-file` (usually next to your `.env` file), so you can always find them.

This makes later review easier:
- You can ask your agent “what happened last time?” and it can use `runs list/show`.
- You don’t need to manually browse folders.

Keep these local files private:
- These artifacts must never include secrets.
- Plans/refusals/audit logs are proof of what happened and that no write was sent.

## Risk levels (guideline)

This tool assigns a conservative risk level per operation name:

- **Low**: operation name starts with `Get*`, `List*`, `Search*`, `Query*`, `Download*`, `Retrieve*`, `Poll*`
- **Medium**: other non-read operations (writes) by default
- **High**: spend/billing-like keywords (budget/bid/billing/payment/invoice/credit/fund/coupon)
- **Irreversible**: delete/remove-like operations

Safety gates enforced (conservative):
- All live calls: require `--live`
- Medium writes: require `--apply`
- High writes: require `--apply --yes --plan-in`
- Irreversible: require `--apply --yes --ack-irreversible --plan-in`
- After those gates, writes require explicit no-snapshot approval before SOAP HTTP when no saved snapshot is available.

High/irreversible actions should require an explicit plan + confirmation.

Irreversible actions should require `--ack-irreversible`.

### Risk gates table (auditable)

| Operation family (heuristic) | Example operation name | Classified risk | Required flags |
|---|---:|---:|---|
| Read-like prefixes | `GetCampaignsByAccountId` | Low | `--live` |
| Non-read default | `AddAccount` | Medium | `--live --apply` |
| Spend/billing keywords | `UpdateBudgets` / `UpdateBidStrategies` | High | `--live --apply --yes --plan-in` |
| Delete/remove-like | `DeleteCampaigns` / `Remove…` | Irreversible | `--live --apply --yes --ack-irreversible --plan-in` |

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

This tool enforces a minimal deterministic drift check when `--plan-in` is provided:
- `env_fingerprint` must match the current env/config
- `request_sha256` (unredacted request JSON hash) must match the current `--request-json` content

## Rollback model (current runtime)

- No built-in rollback is implemented in this runtime.
- write applies require explicit no-snapshot approval before provider writes, so rollback is not needed for the current flow.
- There are no snapshots, backups, or provider restore flows in this runtime.
- If rollback is not possible, label the action as `irreversible_and_clearly_labeled`.
