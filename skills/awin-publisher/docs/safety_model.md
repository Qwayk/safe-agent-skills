# Safety model

Most commands in this tool are remote reads or local file downloads.

- Reads stay explicit. There is no raw request bridge.
- Feed downloads write to local files only when you provide `--out`.
- The tool never prints secrets.
- `proof-of-purchase orders create` is the only remote write command.

## Proof-of-purchase safety

- Default behavior is dry-run.
- Use `--plan-out` to save a reviewable plan.
- Live submission requires `--apply --yes --plan-in`.
- `--plan-in` checks that the file being applied is the same one you planned.
- `--receipt-out` can save the apply receipt.
- Official live use also depends on Awin publisher enablement and advertiser CLO enablement.

## Local proof

- Read commands can log to a JSONL audit file when you ask for it.
- Write commands can also create local run proof under `.state/runs/`.
