# Review a Twilio receipt

Use this after an approved live operation. Share only the private-data-safe plan and receipt; do not paste protected sensitive-output or snapshot files into chat.

```text
Review this Twilio receipt against the approved plan.

Check that:
- the plan ID and fixed command match
- the account fingerprint matches the reviewed environment
- the attempt status is `succeeded`, `failed`, or `uncertain` and matches whether a provider response was received
- when a provider response was received, Twilio returned the expected HTTP result
- when no response was received, the attempt remains uncertain and must be checked before retry
- the provider status is reported literally
- acceptance or queueing is not described as delivery
- the paired read ran when one was available
- the response and verification support the intended outcome
- no unexpected target or effect appears

Return one of: CONFIRMED, NEEDS FOLLOW-UP, or RESULT UNCERTAIN.
Explain what Twilio proved, what it did not prove, and the single safest next action.
If the attempt is uncertain, require a provider-state check before considering another request. Do not propose an automatic retry or rollback. Prepare another reviewed plan only if a real follow-up change is necessary.

Approved plan:
<paste the private-data-safe plan>

Receipt:
<paste the private-data-safe receipt>
```
