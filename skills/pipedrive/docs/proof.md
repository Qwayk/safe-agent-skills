# Proof pack

You do not need to run these commands yourself. They are here for audit and proof.

## Last verified
- 2026-05-22

## Scope
- This tool is read-only only.
- Runtime is aligned to shipped commands in `docs/api_coverage.md`.

## Blessed local validation
- `python3 -m venv .venv`
- `.venv/bin/python -m ensurepip --upgrade`
- `.venv/bin/python -m pip install -e .`
- `.venv/bin/python -m unittest -q`

## Extra spot checks
- `PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --output json --version`
- `PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env onboarding`
- `PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check`
- `PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env --debug --log-file proof_runs.jsonl auth check`

## Example outputs
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/files_download_metadata.json`

## What can go wrong
- Wrong token or domain blocks the connection check, but no CRM data is changed.
- Some read endpoints may still be limited by Pipedrive plan, admin role, or account permissions.
- `files download` stays metadata-only and does not fetch binary bodies.

## Verification notes
- `docs/api_coverage.md` is checked against the shipped command map in tests.
- `tests/test_coverage_smoke.py` runs one safe smoke per command family.
- Example outputs are redacted and checked for the expected runtime shape.

## What is not in scope
- No plan/apply flow.
- No jobs runner.
- No write commands.
