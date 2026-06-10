# API coverage

This page shows exactly what this tool can check today.
If you want to know whether a specific page check is supported, this is the exact list.
It is intentionally small and easy to review.

## Provider

- Provider: Statuspage (Atlassian)
- API base URL: `<STATUSPAGE_BASE_URL>/api/v2/`
- Auth: none (public endpoints)
- Last audited (UTC): 2026-01-26

## Coverage

- [x] `GET /api/v2/status.json` → `statuspage-api-tool status get` — tests: `tests/test_run_artifacts.py`
- [x] `GET /api/v2/summary.json` → `statuspage-api-tool summary get` — tests: `tests/test_run_artifacts.py`
- [x] `GET /api/v2/incidents.json` → `statuspage-api-tool incidents list` — tests: `tests/test_run_artifacts.py`
- [x] `GET /api/v2/scheduled-maintenances.json` → `statuspage-api-tool maintenances list` — tests: `tests/test_run_artifacts.py`
