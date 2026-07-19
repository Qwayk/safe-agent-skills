# Review a Twilio plan

Use this prompt after the tool creates a plan and before any `--apply` command. The target preview hides private values, so the reviewer must inspect the original input file locally as well. Share the plan and the original goal, but never include `.env`, credentials, Authorization headers, or an unredacted provider response.

```text
Review this Twilio operation plan against my goal.

Check that:
- the fixed command is the operation I asked for
- the account fingerprint, region, and edge are the intended environment
- the local input file contains the intended resource or approved recipient
- the plan's input hash binds that exact file content
- the expected effect and risks are complete
- the input has not changed since this plan was created
- the snapshot rule is acceptable, especially if there is no before-state
- the post-apply check can prove the result I care about
- every required acknowledgement is justified
- the receipt destination is new, writable, and protected before HTTP can start
- any bulk target list is exact when checked locally, its derived count matches the intended targets, and the count is no more than 25
- queued, accepted, sent, completed, and delivered will stay separate

Return one of: APPROVE, REPLAN, or DO NOT APPLY.
If APPROVE, list the exact acknowledgement flags and the final apply command.
If REPLAN or DO NOT APPLY, say exactly what is wrong and what must change.

Goal:
<describe the intended Twilio result>

Input file:
<give the local path; inspect private values locally instead of pasting them>

Plan JSON:
<paste the private-data-safe plan>
```

Approval of a plan does not waive consent, recording, identity, compliance, or communications-law requirements.
