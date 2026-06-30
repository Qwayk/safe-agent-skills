# Receipt review prompt

Use this after a live change to check whether the result matched the approved plan.

Safety reminders:
- Do not paste secrets (API keys, tokens).
- If verification failed, do not rollback automatically; review first.

## Prompt

You are reviewing an API tool receipt. A receipt is the record of what the tool actually did.

Inputs:
1) Goal: <paste the user goal / task>
2) Plan JSON (if available): <paste the plan JSON>
3) Receipt JSON: <paste the receipt JSON>

Check:
- Did the tool apply the intended changes (matches the plan)?
- Did verification pass? If not, what failed?
- Any unexpected changes or extra fields modified?
- Is rollback needed? If yes, describe the safest rollback plan.
- If the tool produced backups/snapshots, list what to inspect.

Output:
- Accept or flag issues.
- If issues: propose next action (re-plan, rollback plan, or manual fix).
