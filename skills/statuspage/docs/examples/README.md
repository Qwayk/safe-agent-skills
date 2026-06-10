# Examples (fixed / repeatable)

This folder contains fixed sample JSON responses (no network required) and sample CLI outputs derived from them.

It also contains a small set of static review artifacts used by our orchestrator proof gate. These are not CLI
features or commands.

## Response fixtures

- `status.json` → `GET /api/v2/status.json`
- `summary.json` → `GET /api/v2/summary.json`
- `incidents.json` → `GET /api/v2/incidents.json`
- `scheduled-maintenances.json` → `GET /api/v2/scheduled-maintenances.json`

## CLI outputs

See `outputs/` for sample `--output json` results for each command.

Additional files:
- `outputs/auth_check.json`: informational output example (this tool does not require authentication).
- `plan.example.json`: static plan example (the tool does not implement plan mode).
- `receipt.example.json`: static receipt example (the tool does not implement receipt mode).
