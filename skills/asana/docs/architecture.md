# Architecture

The tool has one generated boundary and one shared runtime path.

## Pinned input and generation

- `specs/asana_oas.yaml` is the official REST specification at the pinned commit.
- `specs/SHA256SUMS` prevents silent input drift.
- `scripts/generate_inventory.py` validates the hash and generates the packaged inventory, manifest, and coverage ledger.
- `src/asana_safe_agent_cli/inventory/operations.json` contains the fixed method, path, parameters, body media type, OAuth scopes, access notes, risk class, snapshot/readback candidate, pagination, and async metadata for all 249 operations.

The generator emits 248 callable commands. It keeps `POST /batch` as the one in-spec exclusion.

## Runtime

- `cli.py` builds argparse choices from the packaged fixed inventory.
- `inventory.py` loads and looks up fixed commands; it cannot construct a new operation.
- `commands/asana.py` validates inputs, runs reads, creates plans, checks approvals and drift, applies writes, verifies when possible, polls returned job GIDs, and saves receipts.
- `config.py` reads the bearer token and fixes the production base URL to Asana.
- `http.py` sends requests, respects bounded retry rules, and keeps headers/query values out of verbose logs.
- `output.py` owns the one-JSON-object stdout contract.
- `audit_log.py` writes optional secret-redacted local events.

Tests inject a fake client through command context. There is no runtime environment variable or flag for changing the production host.

## Local state

Plans and receipts live in `.state` next to the selected env file. They are gitignored. Committed examples under `docs/examples/` use fake GIDs and no secret values.
