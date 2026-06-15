# Safety model

Awin Publisher can touch publisher reporting, link building, feeds, and proof-of-purchase workflows, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Start with a small report or link-builder check, then review the plan before any proof-of-purchase upload."

## Read and file safety

- Accounts, programs, offers, transactions, transaction queries, reports, and linkbuilder commands are read-only.
- Feed commands only write local files when you give an explicit `--out` path.
- Reads stay explicit. There is no raw request bridge.
- The tool never prints secrets.
- `proof-of-purchase orders create` is the only remote write command.

## Proof-of-purchase safety

- Default behavior is dry-run.
- Use `--plan-out` to save a reviewable plan.
- Live submission requires `--apply --yes --plan-in`.
- `--plan-in` checks that the reviewed plan still matches the current environment plus the requested publisher and advertiser ids.
- `--receipt-out` can save the apply receipt.
- Official live use also depends on Awin publisher enablement and advertiser CLO enablement.

## Local proof

- Read commands can log to a JSONL audit file when you ask for it.
- Write commands can also create local run proof under `.state/runs/`.
