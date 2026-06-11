# Proof pack

Last verified (UTC): 2026-02-03

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

## Smoke commands (no secrets required)

Requires Python 3.12+.

- `python3 -m unittest -q`
- `PYTHONPATH=src python3 -m amazon_pa_api_tool --output json --version`
- `PYTHONPATH=src python3 -m amazon_pa_api_tool --output json` (expects `ok=false` JSON + rc=1)

## Committed example outputs

See `docs/examples/outputs/` for redacted, committed example JSON outputs (machine output shapes):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/parse_error_missing_command.json`
- `docs/examples/outputs/auth_check_missing_env.json`
- `docs/examples/outputs/product_get.success.example.json`
- `docs/examples/outputs/product_get.batched.success.example.json`
- `docs/examples/outputs/product_search.success.example.json`
- `docs/examples/outputs/product_variations.success.example.json`
- `docs/examples/outputs/link_build.success.example.json`
- `docs/examples/outputs/browse_get.success.example.json`
- `docs/examples/outputs/jobs_run.success.example.json`

## What can go wrong

- Missing/invalid PA-API credentials: run `amazon-pa-api-tool auth check` after setting `.env` values.
- Argparse/usage errors: in `--output json` mode these return `ok=false` with `error_type=ValidationError`.
