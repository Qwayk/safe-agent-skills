# Proof pack

## Last verified

- Date (UTC): 2026-06-09
- Tool version: 0.1.1
- Base URL: `https://api.awin.com`

## Smoke checks

Run in this folder:

You don’t need to run these commands yourself. They exist for auditing and proof.

1. `python3 -m venv .venv`
2. `.venv/bin/python -m pip install -e .`
3. `.venv/bin/python -m unittest -q`
4. `.venv/bin/python -m awin_advertiser_safe_agent_cli --version` (or `awin-advertiser-safe-cli --version` via script)
5. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json onboarding`
6. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json auth check`
7. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json publishers list --advertiser-id <id>`
8. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions list --advertiser-id <id> --start-date <ISO8601> --end-date <ISO8601>`
9. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions by-ids --advertiser-id <id> --ids <id1,id2>`
10. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions jobs list --advertiser-id <id>`
11. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions jobs show --advertiser-id <id> --job-id <id> [--job-output errors|all]`
12. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json reports publisher --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601>`
13. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json reports campaign --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601> [--campaign <value>] [--publisher-id <id>]`
14. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json conversion orders create --advertiser-id <id> --orders-file <path/to/orders.json>`
15. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json conversion orders create --advertiser-id <id> --orders-file <path/to/orders.json> --apply --yes --ack-irreversible --plan-in <path/to/plan.json> --receipt-out <path/to/receipt.json>`
16. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json offers create --advertiser-id <id> --offer-file <path/to/offer.json>`
17. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json offers create --advertiser-id <id> --offer-file <path/to/offer.json> --apply --yes --ack-irreversible --plan-in <path/to/plan.json> --receipt-out <path/to/receipt.json>`
18. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json product-feeds upload --advertiser-id <id> --vertical retail --locale <token> --feed-file <path/to/feed.jsonl>`
19. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json product-feeds upload --advertiser-id <id> --vertical retail --locale <token> --feed-file <path/to/feed.jsonl> --apply --yes --ack-irreversible --plan-in <path/to/plan.json> --receipt-out <path/to/receipt.json>`
20. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions batch validate --advertiser-id <id> --batch-file <path/to/batch.json>`
21. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions batch validate --advertiser-id <id> --batch-file <path/to/batch.json> --plan-out <path/to/plan.json>`
22. `.venv/bin/python -m awin_advertiser_safe_agent_cli --output json transactions batch validate --advertiser-id <id> --batch-file <path/to/batch.json> --apply --yes --ack-irreversible --plan-in <path/to/plan.json> --receipt-out <path/to/receipt.json>`

## Live verification notes

- This tool is locally tested, documented, and shipped in this repo, but no recorded live run with real Awin advertiser credentials is stored here yet.
- `publishers list`, `transactions list`, `transactions by-ids`, `transactions jobs list`, `transactions jobs show`, `transactions batch validate`, `reports publisher`, `reports campaign`, `offers create`, `product-feeds upload`, and `conversion orders create` are implemented in the shipped CLI surface.
- All relevant read commands keep explicit `--advertiser-id` on the command line.
- Auth behavior differs by endpoint family:
  - `transactions/jobs` endpoints use `Authorization: Bearer <token>` header only.
- `publishers`, `transactions`, `transactions batch validate`, `reports publisher`, and `reports campaign` use both `Authorization: Bearer <token>` and `accessToken=<token>` query.
  - For batch validate, the endpoint docs are ambiguous because they show an `accessToken` header label; this tool resolves that by adding the token both in `Authorization` and query for deterministic behavior in this tool.
- `offers create` and `product-feeds upload` are Bearer-only (no `accessToken` query param).
- `conversion orders create` uses `x-api-key: <AWIN_API_TOKEN>` only and runs in dry-run mode by default.
- The smoke commands above are the local audit baseline for this shipped version. They do not mean live provider verification already happened.
- If required env values are missing, read commands return `blocked: true` and `setup_needed: true` when auth context is unavailable.
- Write requires `--apply --yes --ack-irreversible --plan-in` and supports `--plan-out` and `--receipt-out`.
