# Jobs and batches

Fortnox jobs are intentionally quiet right now. The tool has many explicit Fortnox commands, but it does not ship a generic batch runner that can execute arbitrary rows.

`jobs run` is reserved for future registry-backed Fortnox batch rows. The old template ping rows were removed, and no real public batch registry ships in this tool yet.

Use explicit Fortnox commands one resource at a time so each read, plan, review, apply, and receipt stays tied to a real documented operation.

## Why this stays unsupported

- A generic job runner would make it too easy to hide risky invoice, bookkeeping, payroll, stock, or file actions inside a CSV row.
- Fortnox write behavior depends on the specific resource family, snapshot status, and verification path.
- The safe Fortnox pattern is still explicit command, dry-run plan, reviewed apply, and receipt.

## What to do instead

Ask the agent to choose the exact Fortnox command family for the work, run safe reads first, and create a dry-run plan before any live change. If a future batch feature is added, it should use named registry rows that point back to the same explicit commands and safety gates.
