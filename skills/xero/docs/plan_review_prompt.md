# Review a Xero write plan

Do not paste tokens, client secrets, authorization codes, or private customer data into a chat that is not approved for it.

```text
Review this saved Xero plan against my goal.

Goal:
<what I want changed>

Constraints:
<exact tenant, draft-only rules, records, amounts, dates, and anything that must not change>

Plan:
<protected plan JSON or a safe redacted copy>

Check the auth profile, tenant ID and name, fixed command, method, target URL, input, risk flags, before-state, no-snapshot warning, idempotency key, and verification method. Reject the plan if the target is ambiguous, the scope is wider than my goal, important values are missing, the before-state changed, or the verification is too weak.

If it is safe, state which of --approve, --approve-high-risk, and --ack-no-snapshot are actually required. Do not apply it.
```
