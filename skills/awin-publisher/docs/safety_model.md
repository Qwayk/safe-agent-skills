# How this skill stays safe

Use this page when you want to know what stays read-only, what only writes local files, and what can send a real Awin change.

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
