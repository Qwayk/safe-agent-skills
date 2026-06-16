# API coverage

Freepik coverage shows exactly what the shipped commands can do with image search, licensed downloads, binary fetches, and local inventory files. Start here when an ask sounds possible but you need to know whether it is already shipped, read-only, plan-first, gated, excluded, or outside the tool.

Read the shipped command rows first, then check the excluded or not-yet-live rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether the shipped commands can search images, download licensed results, and show which Freepik workflows are outside the tool."

## Coverage notes

Last verified (UTC): 2026-06-11
This tool intentionally covers a small subset of the Freepik API, optimized for safe preview-first selection and careful licensed downloads.

## Endpoints used

- [x] `GET /resources` → `search images`, `search photos`, `auth check`, `resource related` fallback search
- [x] `GET /resources/{resource_id}` → `resource get`, `resource related` (group extraction), `resource shoot-pack`, `preview`, `download` (safety gates), `search ... --exclude-ai`
- [x] `GET /resources/{resource_id}/download` → `download` with image resize; live apply requires explicit no-snapshot approval before this endpoint
- [x] `GET /resources/{resource_id}/download/{format}` → `download` by format; live apply requires explicit no-snapshot approval before this endpoint

## Behaviors and tests

- [x] Strict JSON output contract (exactly one JSON object to stdout in `--output json`, including parse/usage errors) → `src/freepik_api_tool/cli.py`, `tests/test_cli_json_output_contract.py`
- [x] Download dry-run includes `no_snapshot_available` before-state metadata and an after-apply verification plan → `src/freepik_api_tool/commands/download.py`, `tests/test_download_image_size.py`
- [x] Approved download apply writes the file and inventory row only after explicit no-snapshot approval → `src/freepik_api_tool/commands/download.py`, `tests/test_download_ack_no_snapshot.py`
- [x] Missing no-snapshot approval refuses before provider write → `src/freepik_api_tool/commands/download.py`, `tests/test_download_overwrite_guard.py`
- [x] Batch jobs require `--apply --yes` → `src/freepik_api_tool/commands/jobs.py`, `tests/test_jobs_require_yes.py`
- [x] Fail-closed non‑AI gate (`is_ai_generated=false` AND `has_prompt=false`) → `src/freepik_api_tool/commands/download.py`
- [x] Inventory dedupe guard (refuse re-download unless `--force`) → `src/freepik_api_tool/commands/download.py`, `tests/test_inventory.py`
