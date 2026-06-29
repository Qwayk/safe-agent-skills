# Plan review prompt

Use this when the tool created a plan and you want an AI reviewer to check it before anything changes.

Safety reminders:
- Do not paste secrets (API keys, tokens).
- If the plan touches production or published content, be extra strict.

## Prompt

You are reviewing an API tool plan. An API is the official connection to the service. Your job is to check whether the plan matches the user's real goal and is safe to apply.

Inputs:
1) Goal: <paste the user goal / task>
2) Constraints: <draft-only? no deletes? specific fields?>
3) Plan JSON: <paste the plan JSON>

Check:
- Target correctness: does the selector match the intended resource?
- Risk correctness: is the risk level appropriate? Is `--yes` required?
- Preconditions: are they strict enough to prevent wrong applies?
- Scope: does the plan change only what is intended (no extra edits)?
- Safety: does the plan avoid irreversible actions unless explicitly intended?
- Verification: does the plan include read-back/idempotence checks?
- Rollback: is rollback possible? If not, is that clearly stated?

Output:
- Approve or reject.
- If reject: explain exactly what to change in the plan.
- If approve: restate the exact apply command to run (including flags).
