# Safety model

Rules:
- Local writes are split by command family:
  - Tracked write flows use dry-run by default, require `--apply`, and require explicit no-snapshot approval when no saved snapshot is available.
  - Local immediate flows write right away (no `--apply`), and must be cleaned up manually if needed.
- tracked write applies require explicit no-snapshot approval before provider write HTTP, local download file writes, or stub receipt output when no saved snapshot is available.
- Refuse when unsure; do not guess.
- Batch jobs require `--apply` and `--yes`.
- Never log secrets.

Tracked write flows in this tool:
- `photos download`
- `jobs run`
- `demo write`

Local immediate flows in this tool:
- `export ... --out ...` (writes local JSON)
- `auth key set --file ...` (writes `.state/auth.json`)
- `onboarding` (writes `.env` unless `--no-write-env`)

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- tracked writes require explicit no-snapshot approval before apply and expose `no_snapshot_available` before_state metadata.
- When approval is missing for a no-snapshot write, the tool must label that clearly and refuse.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply → Verify

Recommended workflow for tracked writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Try apply with `--apply` (and `--yes` for risky actions) only after approval.
4) Report the explicit no-snapshot approval; for missing-approval refusals, confirm no provider write; for approved applies, confirm the receipt records the no-snapshot approval.

## Plans and receipts (recommended)

For tracked write commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen
- explicit no-recovery contract under `recovery`:
  - `end_state: "irreversible_and_clearly_labeled"`
  - `strategy: "no_inverse"`
  - `rollback_ready: false`
  - `automatic_rollback: false`
  - `backups: []`
  - `snapshots: []`
  - `rollback_plan: null`
  - `restore_note` describing manual cleanup when relevant

Missing-approval refusal for tracked writes:
- `refused: true`
- `before_state.status: "no_snapshot_available"`
- a verification plan that confirms no provider write, local download file write, or successful write receipt happened

Approved apply receipts for tracked writes must record explicit no-snapshot approval and recovery limits.

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

For tracked write commands that support plan/apply, this template also recommends:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>` is for approved post-apply receipt JSON; missing-approval refusals do not write it

This makes the workflow repeatable in CI and easier to review.

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
- Plans/refusals/audit logs are proof of what happened and why the write did not proceed.

## Risk levels (guideline)

- Low: create new drafts; small safe edits.
- Medium: edit an existing draft; single-resource updates.
- High: edit published content; status changes; deletes; batch.
- Irreversible: actions that cannot realistically be undone (example: analytics events, licensing downloads).

High/irreversible tracked actions should require an explicit plan + confirmation.

Note on this tool:
- `photos download --apply` would trigger Unsplash download tracking if enabled, so source requires explicit no-snapshot approval before that endpoint when no saved snapshot is available.
- Tracked write plans use the explicit no-recovery contract and show `recovery.strategy="no_inverse"`.

For irreversible actions, consider an extra acknowledgement flag:
- `--ack-irreversible`

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Rollback (recommended default)

- Do not auto-rollback silently.
- If verification fails and rollback is possible, generate a rollback plan and require explicit apply.
- If rollback is not possible, label `recovery.strategy = "no_inverse"` and the manual cleanup path in `recovery.restore_note`.
