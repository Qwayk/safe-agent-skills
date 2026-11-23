# Awin Advertiser test results

## November 23, 2026 local checks

Fresh CLI installs from the source and the local release copy each passed 84 tests with the network blocked. The local skill installer copied all 66 release files under `awin-advertiser-safe-cli` in a temporary Codex skills folder.

The tests ran the quickstart and checked that an explicit settings file controls the account. All four write commands refused a changed token. The tests also covered changed input, older plans, pending and partly failed orders, rejected transactions, feed version and product count, and an unclear reply that left a receipt without resending the request.

## June 11, 2026 checks

- Date (UTC): 2026-06-11
- Tool version: 0.1.1
- Base URL: `https://api.awin.com`

### Commands from the June record

The June record listed these commands. Use the [current quickstart](quickstart.md) or [command guide](command_reference.md) for setup and new work.

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

## Live access

No run with real Awin advertiser credentials is recorded here. The [coverage page](api_coverage.md) explains the endpoint limits. The JSON in [example outputs](examples/outputs/) shows earlier tool versions.
