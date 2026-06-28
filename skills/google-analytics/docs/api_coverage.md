# API coverage

Google Analytics coverage shows exactly what this skill can do with GA4 properties, reports, audiences, links, and admin settings. Start here when an ask sounds possible but you need to know whether it is already shipped, read-only, plan-first, gated, excluded, or outside the tool.

Read the shipped command rows first, then check the excluded or not-yet-live rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether this skill can run this GA4 report, inspect this property, and show which admin changes are covered."

## Coverage notes

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
- Coverage source of truth: the vendored discovery snapshots under `src/ga4_api_tool/_vendor/`
- Last audited (UTC): 2026-03-03

## Known gaps

- None relative to the vendored snapshots.

Notes:
- If Google adds/removes methods upstream, this tool will only change when we update the vendored discovery JSON and the committed inventories.
