# Proof and verification

You do not need to run these commands yourself. They exist for auditing and proof.

## Last verified

- Date (UTC): 2026-06-11
- Tool version: 0.1.0
- Version check passed: `.venv/bin/awin-publisher-safe-cli --output json --version`
- Validation command passed: `python3 -m venv .venv && .venv/bin/python -m pip install -e . && .venv/bin/python -m unittest -q`
- This validation command was rerun after the README UX rebuild and docs contract test pass, and it passed.
- Live Awin credential proof has not been run yet.
- Proof-of-purchase live proof is still blocked here until Awin enables the publisher and the advertiser enables CLO for that program.
- Environment: local build env

## Smoke checks

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/awin-publisher-safe-cli --output json --version
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json auth check
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json accounts list
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json offers list --publisher-id <publisher_id>
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json transactions list --publisher-id <publisher_id> --start-date 2026-06-01T00:00:00Z --end-date 2026-06-02T00:00:00Z --timezone UTC
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json reports advertiser --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json linkbuilder quota --publisher-id <publisher_id>
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json feeds enhanced-download --publisher-id <publisher_id> --advertiser-id <advertiser_id> --locale en_GB --out enhanced-feed.jsonl
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json --plan-out proof-plan.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json
.venv/bin/python -m unittest -q
```

If live proof-of-purchase access is approved later, the live command must reuse the reviewed plan file:

```bash
.venv/bin/python -m awin_publisher_safe_agent_cli.cli --output json --apply --yes --plan-in proof-plan.json --receipt-out proof-receipt.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json
```

## What can go wrong

- Awin has mixed `/publisher` and `/publishers` paths, so drift in docs or code can break one family while another still works.
- Legacy product feed helpers depend on the separate feed API key and legacy host.
- The proof-of-purchase endpoint is live-writing, requires the saved plan file for apply, and still needs Awin-side publisher enablement plus advertiser-side CLO enablement before a real live proof run is possible.

## Honest limits

- This repo currently proves proof-of-purchase only in dry-run and mocked HTTP tests.
- No live proof-of-purchase success is recorded yet.
- The official proof-of-purchase page rechecked on 2026-06-09 says both activation steps are required before live use.

## Example outputs

- `docs/examples/outputs/accounts_list.json`
- `docs/examples/outputs/programs_list.json`
- `docs/examples/outputs/offers_list.json`
- `docs/examples/outputs/transactions_list.json`
- `docs/examples/outputs/reports_campaign.json`
- `docs/examples/outputs/linkbuilder_generate.json`
- `docs/examples/outputs/feeds_enhanced_download.json`
- `docs/examples/outputs/proof_of_purchase_orders_create_plan.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
