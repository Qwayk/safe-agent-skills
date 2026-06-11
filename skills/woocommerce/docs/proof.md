# Proof

You don’t need to run these commands yourself.
They exist for auditing and proof.

## Last checked

- Date (UTC): `2026-06-04`
- Scope: local packaging, catalog generation, onboarding, file-based input options, planning, explicit no-snapshot approval, and artifact/log controls
- Live store writes: not verified in this repo run because no store credentials were provided
- Recovery note: write operations include rollback notes and explicit `before_state` fields in plans. write apply requires explicit no-snapshot approval before WooCommerce HTTP when no saved snapshot is available and produces a receipt only after the required approval path.

## Local proof commands

```bash
.venv/bin/python -m unittest -q
.venv/bin/python -m unittest -q tests.test_docs_formatting
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --output json --version
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --output json operations list
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --env-file .env.example --output json onboarding --no-write-env
cat > /tmp/coupon-body.json <<'JSON'
{"code":"SAVE10","discount_type":"percent","amount":"10"}
JSON
cat > /tmp/coupon-params.json <<'JSON'
{"search":"SAVE10"}
JSON
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --env-file .env.example --output json --plan-out /tmp/woo-plan.json coupons create --body-json '{"code":"SAVE10","discount_type":"percent","amount":"10"}'
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --env-file .env.example --output json coupons create --body-file /tmp/coupon-body.json --params-file /tmp/coupon-params.json
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --env-file .env.example --output json --artifacts-dir /tmp/woo-run --log-file /tmp/woo-audit.jsonl coupons create --body-json '{"code":"SAVE10","discount_type":"percent","amount":"10"}'
PYTHONPATH=src python3 -m qwayk_woocommerce_safe_agent_cli --env-file .env.example --output json --apply --plan-in /tmp/woo-plan.json coupons create --body-json '{"code":"SAVE10","discount_type":"percent","amount":"10"}'
```

Latest local result:
- full suite: `26 tests, OK`
- docs formatting: `2 tests, OK`
- operations inventory smoke: `139` operations
- JSON examples: `docs/examples/plan.example.json` and `docs/examples/receipt.example.json` parsed successfully

## What can go wrong

- Missing or wrong REST keys will block live API calls.
- Some servers strip `Authorization` headers; use `WOOCOMMERCE_QUERY_STRING_AUTH=true`.
- High-risk writes can change customer-facing store behavior, emails, or checkout settings.
- write apply requires explicit no-snapshot approval before provider HTTP when no operation-specific saved snapshot is available.

## Example outputs

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/operations-list.json`
- `docs/examples/outputs/onboarding.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; old filename kept)
