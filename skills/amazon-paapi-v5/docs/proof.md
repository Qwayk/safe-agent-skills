# Proof and verification

Amazon Product Advertising API proof should answer a simple question: what has actually been checked for product lookup and browse-node research, and what still depends on account access, provider permissions, public API limits, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check the version/auth examples and one product or browse-node output before trusting product data.

## Current proof summary

Last verified (UTC): 2026-02-03

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
