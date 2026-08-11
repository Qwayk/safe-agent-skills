# API coverage

This is the honest list of what the tool covers today. The scope is complete for the chosen official GiantPanda Parking API family and excludes everything else.

## Summary

- Provider: GiantPanda Parking API
- API base URL: `https://account.giantpanda.com`
- Auth method: `Authorization: Token <GIANTPANDA_API_TOKEN>`
- Build strategy: `manual-family build required`
- Last audited (UTC): 2026-08-11

## Endpoint coverage

| Endpoint | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| `GET /api/v1/domains/stats/` | Read parking stats for a date window, grouped by date and domain | `domains stats` | read-only; fixed host + required auth | `tests/test_domains_stats.py`, `docs/examples/outputs/stats.json` | Implemented, locally tested, and provider-live verified on 2026-08-11 with one installed-wheel request: HTTP 200 and an object response with top-level keys `end_date`, `pagination`, `start_date`, and `stats`. |
| `POST /api/v1/domains/add/` | Add one or more domains after normalization and validation | `domains add` | `--dry-run` default; write requires `--apply`, `--plan-in`, `--approve-plan`, `--ack-no-snapshot` | `tests/test_domains_add.py`, `docs/examples/plan.example.json`, `docs/examples/receipt.example.json` | Implemented in source; local-dry run and mocked apply verified. Provider-live response/side effects remain `implemented, provider-live-unverified` under manual-family build. |

## Known gaps

- No other GiantPanda API operation families are in scope for this tool build.
