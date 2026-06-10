# Proof

You do not need to run these commands yourself. They are here for proof and audit.

## Last verified

- Date (UTC): `2026-05-21`
- Scope: free TheMealDB V1 public read endpoints only
- Validation command: `python3 -m venv .venv && .venv/bin/python -m pip install -e . && .venv/bin/python -m unittest -q`
- Validation result: `16 tests passed`

## Smoke commands

- `qwayk-themealdb-safe-agent-cli --output json --version`
- `qwayk-themealdb-safe-agent-cli --output json auth check`
- `qwayk-themealdb-safe-agent-cli --output json categories`
- `qwayk-themealdb-safe-agent-cli --output json search name --name Arrabiata`
- `qwayk-themealdb-safe-agent-cli --output json lookup id --meal-id 52772`
- `qwayk-themealdb-safe-agent-cli --output json filter category --category Seafood`

## Example outputs

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/categories.json`
- `docs/examples/outputs/list_categories.json`
- `docs/examples/outputs/list_areas.json`
- `docs/examples/outputs/search_name_arrabiata.json`
- `docs/examples/outputs/lookup_52772.json`
- `docs/examples/outputs/filter_category_seafood.json`
- `docs/examples/outputs/filter_area_canadian.json`
- `docs/examples/outputs/filter_ingredient_chicken_breast.json`
- `docs/examples/outputs/random.json`

## What can go wrong

- Network failure or vendor outage
- Zero-result searches or filters
- Invalid custom API key
- Large payload from `list ingredients`

## Verification notes

- Unit tests cover the command families and JSON error handling.
- Auth-path safety tests confirm custom API keys are redacted from error output.
- Live example outputs were captured from the real API using the public key `1`.
