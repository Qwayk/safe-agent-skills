# Architecture

WooCommerce is built as a small command-line tool for products, orders, customers, coupons, reports, and store settings. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches WooCommerce.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for WooCommerce."

## Runtime layers

- `catalog.py` is the main reference for official WooCommerce v3 operations.
- `cli.py` builds explicit command families from that catalog.
- `client.py` and `http.py` handle auth, request transport, and redaction.
- `commands/operations.py` handles read execution, dry-run plans, and explicit no-snapshot approval for write apply.
- `docs/api_coverage.md` is generated from the shipped catalog.
