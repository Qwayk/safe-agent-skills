# Receipt review prompt

Use this prompt style after apply for a GiantPanda domain add.

## Reviewer prompt

You are checking a receipt against the approved plan.

Inputs:

- User goal
- Approved plan JSON
- Receipt JSON

Check:

- Plan id match between plan and apply output
- `provider` host and endpoint are fixed GiantPanda host and `/api/v1/domains/add/`
- Request body contains exactly normalized domains and no extra fields
- Receipt mode is `0600` (check the file mode on disk; mode is not in JSON)
- Verification is available and was parsed, or if not parsed, uncertainty is explicitly present

Output:

- `accept` when the apply path matched,
- `investigate` when verification was unavailable, no-snapshot warning was missed, or provider response does not match plan metadata.
