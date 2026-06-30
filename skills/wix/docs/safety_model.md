# Safety model

This page explains how the skill helps you move carefully: look first, think second, and change last.

For everyday work, that means safe checks can run right away, but bigger changes should pause for review before anything live happens.

## What safe use looks like

- Safe checks do not change anything.
- Changes should start with a preview.
- Bigger or riskier work should wait for approval.
- The tool should leave a clear record of what it checked and what changed.
- Secrets should stay out of logs, plans, receipts, and chat.

## Why some work takes longer

Some actions are easy to review and reverse. Others are public, permanent, or hard to undo.

A good tool should treat those cases differently instead of pushing every action through at the same speed.

## Normal change flow

1. Generate a preview or plan.
2. Review the target and the proposed change.
3. Apply only after clear approval.
4. Verify what happened.
5. Save a receipt for later review.

## What plans and receipts are for

A plan shows:
- what the tool wants to change
- what needs to be true before it is safe
- how the tool plans to verify the result

A receipt shows:
- what actually changed
- what verification ran
- where to find any useful follow-up proof

Plans and receipts must never include secrets.

## Common safety rules

- Dry-run should be the default.
- No writes should happen unless the user clearly approves them.
- Batch work should require a stronger confirmation than one small change.
- The tool should refuse when the target is unclear or the risk is too high.
- After a live change, the tool should verify the result when the provider allows it.

## Run history

For write-capable commands, the Wix safe CLI writes a local run folder under `.state/runs/` and adds a simple history row to `.state/runs/index.jsonl`.

That history is there so the user or agent can answer simple questions later, like what changed last time or whether verification passed.

## Higher-risk actions

Some actions deserve extra friction:
- big batch changes
- deletes or status flips
- published content changes
- actions that are hard to undo

Those actions should require a stronger plan-and-approval step than a simple read or small draft edit.

## If the target changes after planning

If the tool supports applying from a saved plan, it should refuse when the target changed since the plan was created.

Examples include:
- a newer `updated_at` or `modified_gmt` value
- a changed content hash

## Rollback

- Do not auto-rollback silently.
- If verification fails and rollback is possible, generate a rollback plan and require explicit approval.
- If rollback is not possible, label the action as hard to undo before the user approves it.
