# Cloudinary test results

## November 23, 2026

Installed both local packages in fresh Python environments. Each loaded all 175 commands and passed 42 tests. With simulated Cloudinary replies, I checked the selected settings file, a video read with media credentials, and all 98 write commands with and without their saved plans.

The upload checks covered a replaced local file and an intentional overwrite. The metadata check confirmed the tool sent the reviewed JSON and checked whether the name matched afterward. The deletion checks distinguished a missing asset from a denied or failed lookup. The access-key check kept the returned test secret in the private output file. It did not appear in the terminal output or receipt.

Live account access and changes were not part of these checks. Use the current approval steps in [Approve and check changes](safety_model.md).

## June 4, 2026 source checks

Original test date (UTC): 2026-06-04
Tool version: `0.1.0`

## Commands run

```bash
python3 scripts/generate_cloudinary_rest_inventory.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m cloudinary_safe_agent_cli --output json --version
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m cloudinary_safe_agent_cli --output json operations list --area upload --limit 3
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m cloudinary_safe_agent_cli --env-file .env.example --output json auth check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest -q

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest -q tests/test_operations_parser.py tests/test_admin_operations.py tests/test_upload_operations.py
```

## Results

- generated inventory and coverage report completed
- runtime allowlist count: 175 operations
- version command returned the expected tool name and version
- operations discovery command returned upload operations
- `auth check` ran safely against `.env.example` and reported setup status without leaking secrets
- the focused write-safety suites passed (`14 tests, OK`)
- the full unit test suite passed (`37 tests, OK`)
- docs formatting passed (`1 test, OK`)
- committed JSON examples under `docs/examples/` parsed successfully
- write apply attempts now require explicit no-snapshot approval before Cloudinary HTTP when no saved snapshot is available
- `docs/examples/receipt.example.json` now records the current write-refusal shape, not a successful write receipt
- final polish removed shipped scaffold leftovers and cleaned local runtime folders before closeout

## Known live limits

- local tests are doc-driven and mocked; real Cloudinary credentials are still needed for live endpoint verification
- provisioning and most permissions commands depend on Cloudinary account access and plan gates
- Analyze API commands are shipped from official docs, but some are beta and may require extra Cloudinary enablement
- No generic rollback or snapshot restore command is exposed. Backup download is read-only; restore and backup-delete writes currently require explicit no-snapshot approval before Cloudinary HTTP when no saved snapshot is available.
