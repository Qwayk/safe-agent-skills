# Architecture

The n8n source tool has three main pieces.

## Inventory

- `docs/specs/n8n-public-api-v1-2026-06-29/`: pinned official n8n public API spec folder.
- `docs/official_inventory.json`: generated review copy of the 80-operation inventory.
- `src/n8n_safe_agent_cli/data/official_inventory.json`: runtime copy used by the CLI.

## Runtime

- `cli.py`: shared flags, run history, and generated `api <family> <command>` parser.
- `commands/api.py`: read execution, dry-run plans, plan matching, live apply, receipts, and response redaction.
- `commands/auth.py`: read-only connection check.
- `commands/onboarding.py`: local setup helper.
- `config.py`: `.env` parsing and API-key fingerprinting.
- `http.py`: small `requests` wrapper.
- `sanitize.py`: output redaction.
- `runs.py`: local run folders and `.state/runs/index.jsonl`.

## Safety Shape

The parser exposes official operation commands from the inventory. There is no raw request command. Writes are identified from the HTTP method and are forced through the plan-review-apply path.
