# Proof pack (publish-ready evidence)

Purpose:
- Make this tool proof-first for future customer pages and reviews.
- Capture the small set of checks a reviewer can trust: what ran, what passed, and what still depends on live HubSpot access.

You do not need to run these commands yourself. They exist for auditing and proof.

Rules:
- Never include secrets.
- Use clear redactions or placeholders in committed examples.
- Keep this file short and factual.
- HubSpot live writes currently require explicit no-snapshot approval before HTTP when no saved snapshot is available.
- This tool does not use snapshots, provider backups, or automatic rollback.
- Proof is local-only via plan, receipt, refusal, and local artifact output.

## Last verified

Date (UTC): `2026-06-04`
Verified by: `qwayk-hubspot-safe-agent-cli maintainers`
Tool version: `0.1.0`
Environment: `local portfolio-build` / base URL: `https://api.hubapi.com`

## Smoke checks (copy/paste)

Run inside the tool folder:

1. Create venv + install:
   - `python3 -m venv .venv`
   - `.venv/bin/python -m pip install -e .`
2. Version (no `.env` required):
   - `.venv/bin/qwayk-hubspot-safe-agent-cli --output json --version`
3. Guided setup without live creds:
   - `.venv/bin/qwayk-hubspot-safe-agent-cli --output json onboarding`
4. Auth check with live creds only:
   - `.venv/bin/qwayk-hubspot-safe-agent-cli --output json auth check`
5. One safe write preview:
   - `.venv/bin/qwayk-hubspot-safe-agent-cli --plan-out plan.json hubspot objects create --object-type contacts --body-file body.json`
6. One missing-approval write refusal:
   - `.venv/bin/qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot objects archive --object-type contacts --object-id 123`

## Commands run in this portfolio build

- `PYTHONPATH=src python3 -m unittest tests.test_command_families tests.test_hubspot_safety tests.test_hubspot_import_validation tests.test_run_artifacts tests.test_onboarding_command tests.test_auth_redaction tests.test_imports`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m hubspot_safe_agent_cli --output json --version`
- `PYTHONPATH=src python3 -m hubspot_safe_agent_cli --output json --env-file "$tmpdir/.env" onboarding`
- `PYTHONPATH=src python3 -m hubspot_safe_agent_cli --env-file "$tmpdir/.env" hubspot objects create --object-type contacts --body-file "$tmpdir/body.json"`

Latest full local test result:
- `27` tests passed with `.venv/bin/python -m unittest -q`

## Example outputs (redacted)

These files are committed:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; approved supported writes emit receipts)

## What can go wrong (and how we verify)

- Missing token or wrong scopes: `auth check` should refuse cleanly or fail with a non-secret message, and no write should happen.
- Rate limiting: verify the CLI returns the provider error clearly and does not hide it behind generic output.
- Pagination surprises: verify read results keep HubSpot paging data intact.
- Write safety drift: verify risky writes still require `--apply`, `--yes`, `--ack-irreversible`, and `--plan-in` where documented, then require explicit no-snapshot approval before HubSpot HTTP when no useful before-state can be saved.

## Portfolio-build status

This tool is ready for local read use, local dry-run proof, missing-approval refusal proof, and approved supported write receipts when live access is available.
Live HubSpot proof still depends on:
- local auth available in `HUBSPOT_ACCESS_TOKEN` or stored OAuth JSON
- account-level scopes for the endpoints you call
- active object types and account tier in your HubSpot portal

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
