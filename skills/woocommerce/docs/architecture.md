# Architecture

- `catalog.py` is the source of truth for official WooCommerce v3 operations.
- `cli.py` builds explicit command families from that catalog.
- `client.py` and `http.py` handle auth, request transport, and redaction.
- `commands/operations.py` handles read execution, dry-run plans, and explicit no-snapshot approval for write apply.
- `docs/api_coverage.md` is generated from the shipped catalog.
