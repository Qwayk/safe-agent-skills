# Public API routes

The tool reads these four routes from a public Atlassian Statuspage site. They work without credentials. The [command guide](command_reference.md) explains the difference between a current check and recent history.

Last API audit recorded before this cleanup (UTC): 2026-06-11. See the [test results](proof.md) for later checks.

| Public route | CLI command |
| --- | --- |
| `GET /api/v2/summary.json` | `statuspage-api-tool summary get` |
| `GET /api/v2/status.json` | `statuspage-api-tool status get` |
| `GET /api/v2/incidents.json` | `statuspage-api-tool incidents list` |
| `GET /api/v2/scheduled-maintenances.json` | `statuspage-api-tool maintenances list` |

[The command tests](../tests/test_run_artifacts.py) check the request and reply for each route. Use the [public Status API docs](https://status.atlassian.com/api) for the provider’s field and route descriptions.
