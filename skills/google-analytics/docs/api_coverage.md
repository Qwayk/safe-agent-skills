# API coverage (method ids → CLI)

This tool’s “100% coverage” definition is:

- 100% of **method ids** present in the **vendored discovery snapshots** are available as explicit CLI commands.

Canonical inventories (committed, deterministic):

- `docs/official_methods_admin_v1alpha.txt` (164 method ids)
- `docs/official_methods_data_v1beta.txt` (11 method ids)
- `docs/official_methods_data_v1alpha.txt` (13 method ids)
- `docs/official_commands.txt` (188 explicit commands)

Tests enforce coverage:

- `tests/test_discovery_coverage.py`
- `tests/test_cli_method_registration.py`

## Summary

- Provider: Google Analytics 4 (GA4)
- APIs: Analytics Admin API + Analytics Data API
- Coverage main reference: the vendored discovery snapshots under `src/ga4_api_tool/_vendor/`
- Last audited (UTC): 2026-03-03

## Known gaps

- None relative to the vendored snapshots.

Notes:
- If Google adds/removes methods upstream, this tool will only change when we update the vendored discovery JSON and the committed inventories.
