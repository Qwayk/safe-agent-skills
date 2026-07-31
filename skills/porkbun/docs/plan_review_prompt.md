# Plan review prompt

Use this after a command plan is generated and before apply.

## Prompt

You are reviewing a Porkbun plan.

Inputs:
1) Goal:
2) Constraint notes:
3) Plan JSON:

Check:
- target resource and selector are correct
- risk is correctly classified
- required approval flags are listed (`--ack-*`, `--yes`, `--apply`)
- whether `--secret-out` is required for secret-bearing commands
- whether `agreeToTerms` is required and present for domain registration
- before-state capture behavior is stated
- readback and verification path is clear

Output:
- Approve or reject
- If reject, list exact plan fixes needed
