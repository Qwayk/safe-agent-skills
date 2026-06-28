# Proof and verification

Most users will never need to run these commands themselves. You don’t need to run these commands yourself. They exist so a reviewer can check what has actually been checked, what was only tested locally, and what still needs live Azure credentials before anyone treats a result as proved. If you only check one thing, check that a run left a clear plan, receipt, refusal, or example output that matches the action the agent says it performed.

## Current proof summary

- The Azure command catalog is generated from a pinned Azure REST API spec snapshot.
- Source tests cover command docs, auth behavior, write gates, sensitive-read redaction, jobs behavior, and inventory shape.
- Local examples are redacted and do not contain real Azure secrets.
- Live Azure behavior is marked honestly when it has not been checked against safe credentials and a real target.

## What this page proves

- The Azure CLI source shape is documented.
- Inventory metadata is pinned and stored in `docs/official_inventory.json`.
- Safety gates and command flow are present in command docs.

## Local proof evidence

Run these checks from the tool folder after dependencies are installed:

```bash
qwayk-azure-safe-agent-cli --output json --version
qwayk-azure-safe-agent-cli onboarding --no-write-env
qwayk-azure-safe-agent-cli auth check
qwayk-azure-safe-agent-cli inventory summary
```

These commands can be run without changing Azure. They prove local command startup, local setup shape, auth readiness reporting, and inventory availability.

## What is still live-unverified

- `auth check` confirms local configuration state and token presence.
- Live Azure execution is not verified in this repo snapshot without live credentials.
- Write verification notes in receipts depend on the real target response path.

## Artifact locations

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
- `.state/runs/*` when write-capable commands are run

The checked-in examples are redacted, representative examples from this Azure CLI shape. They do not claim live Azure account proof.

## Safety proof

- Refusals are expected for these conditions:
  - missing `AZURE_API_TOKEN`
  - missing `AZURE_DATA_PLANE_ENDPOINT` on data-plane command
  - write commands without `--plan-in`, `--apply`, `--yes`
  - missing `--ack-no-snapshot` / `--ack-irreversible` where required
  - plan drift
  - demo or jobs write apply paths, which are local-only and do not apply Azure writes

Sensitive-read proof is covered by tests that mark secret-like reads in `docs/official_inventory.json` and redact generic response fields such as `value`.
