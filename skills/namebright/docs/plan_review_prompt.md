# Plan review prompt

Use this when the tool created a plan and you need a review before apply.

Safety reminder: do not paste secrets (API keys, tokens, verification codes).

## Prompt

You are reviewing a NameBright plan.

Inputs:
1) Goal: <paste the user goal / task>
2) Constraints: <if any>
3) Plan JSON: <paste the plan JSON>

Check:
- Target correctness: does the plan command match the user goal?
- Required acknowledgements: are all required for this command and no extra?
- Preconditions and scope: are target identifiers and values exact and narrow?
- Verification plan: are read-back commands listed for expected changes?
- Snapshot risk: if `no_snapshot` applies, is the action explicitly described as irreversible?

Output:
- Approve or reject.
- If reject: explain what must change.
- If approve: restate the exact `--apply` command to run.
