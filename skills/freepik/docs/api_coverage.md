# API coverage

Last verified (UTC): 2026-06-04

This tool intentionally covers a small subset of the Freepik API, optimized for safe preview-first selection and audited download planning.

## Endpoints used

- [x] `GET /resources` → `search images`, `search photos`, `auth check`, `resource related` fallback search
- [x] `GET /resources/{resource_id}` → `resource get`, `resource related` (group extraction), `resource shoot-pack`, `preview`, `download` (safety gates), `search ... --exclude-ai`
- [x] `GET /resources/{resource_id}/download` → `download` planned only; current apply requires explicit no-snapshot approval before this endpoint
- [x] `GET /resources/{resource_id}/download/{format}` → `download` planned only; current apply requires explicit no-snapshot approval before this endpoint

## Behaviors and tests

- [x] Strict JSON output contract (exactly one JSON object to stdout in `--output json`, including parse/usage errors) → `src/freepik_api_tool/cli.py`, `tests/test_cli_json_output_contract.py`
- [x] Download dry-run includes blocked `before_state`; current apply requires explicit no-snapshot approval before provider write when no saved snapshot is available → `src/freepik_api_tool/commands/download.py`, `tests/test_download_image_size.py`
- [x] Future enabled download path refuses overwrites unless `--force` → `src/freepik_api_tool/commands/download.py`, `tests/test_download_overwrite_guard.py`
- [x] Batch jobs require `--apply --yes` → `src/freepik_api_tool/commands/jobs.py`, `tests/test_jobs_require_yes.py`
- [x] Fail-closed non‑AI gate (`is_ai_generated=false` AND `has_prompt=false`) → `src/freepik_api_tool/commands/download.py`
- [x] Inventory dedupe guard (refuse re-download unless `--force`) → `src/freepik_api_tool/commands/download.py`, `tests/test_inventory.py`
