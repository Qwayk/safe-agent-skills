# Receipt review prompt

Use this after a live change to confirm the action matched the approved plan.

Safety reminder: do not paste secrets (API keys, tokens, verification codes).

## Prompt

You are reviewing a NameBright receipt. A receipt records what the tool actually ran.

Inputs:
1) Goal: <paste the user goal / task>
2) Plan JSON (if available): <paste the plan JSON>
3) Receipt JSON: <paste the receipt JSON>

Check:
- Did the tool apply the exact plan target and values?
- Did `write.ok` and `verification.ok` match the expected outcome?
- Are any verification results failed or marked with `note` entries?
- Are there unexpected fields or side effects in `write.response`?
- If verification failed, give the safest next action (replan, manual inspect, or safe follow-up read).

Output:
- Accept or flag issues.
- If issues: name the exact gap and the next manual step.
