# Jobs and Batches

AWS batch work should stay boring and reviewable: one clear target, one named operation, one plan or receipt at a time.

This tool does not ship a separate background worker. Each command runs in one process.

## How to handle repeated AWS work

- Keep the loop explicit.
- Use named AWS service commands.
- Run reads first when possible.
- For writes, create and review plans before apply.
- Do not hide many destructive targets behind one vague instruction.
- Stop on the first unexpected refusal, access error, or verification limit.

## Why this matters

AWS batch mistakes can multiply quickly across regions, accounts, buckets, instances, queues, users, or policies. Keeping each target visible makes it easier to catch the wrong account, wrong region, missing permission, or high-risk operation before apply.

The local proof for write-capable commands lives under `.state/runs/`.
