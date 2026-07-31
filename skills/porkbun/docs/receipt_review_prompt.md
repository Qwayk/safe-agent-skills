# Receipt review prompt

Use this after an apply completes.

## Prompt

You are reviewing a Porkbun receipt.

Inputs:
1) Goal:
2) Plan JSON:
3) Receipt JSON:

Check:
- final apply command matches the plan
- ack flags and risk gates were present
- changed keys and summary match expected scope
- any secret-bearing output is not printed in plain text output
- readback verification is actually performed where possible
- write confirmation is clearly marked when only status confirmation exists

Output:
- Accept or flag issues
- If issues: what to fix in the run or next command
