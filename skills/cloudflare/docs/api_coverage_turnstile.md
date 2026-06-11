# Turnstile widgets endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_turnstile.csv

Regenerate:
```bash
python3 scripts/generate_turnstile_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/challenges/widgets` | `accounts-turnstile-widgets-list` | List Turnstile Widgets | Turnstile |  | cloudflare-api-tool operations turnstile accounts-turnstile-widgets-list | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/challenges/widgets` | `accounts-turnstile-widget-create` | Create a Turnstile Widget | Turnstile |  | cloudflare-api-tool operations turnstile accounts-turnstile-widget-create | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | DELETE | `/accounts/{account_id}/challenges/widgets/{sitekey}` | `accounts-turnstile-widget-delete` | Delete a Turnstile Widget | Turnstile |  | cloudflare-api-tool operations turnstile accounts-turnstile-widget-delete | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/challenges/widgets/{sitekey}` | `accounts-turnstile-widget-get` | Turnstile Widget Details | Turnstile |  | cloudflare-api-tool operations turnstile accounts-turnstile-widget-get | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PUT | `/accounts/{account_id}/challenges/widgets/{sitekey}` | `accounts-turnstile-widget-update` | Update a Turnstile Widget | Turnstile |  | cloudflare-api-tool operations turnstile accounts-turnstile-widget-update | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/challenges/widgets/{sitekey}/rotate_secret` | `accounts-turnstile-widget-rotate-secret` | Rotate Secret for a Turnstile Widget | Turnstile |  | cloudflare-api-tool operations turnstile accounts-turnstile-widget-rotate-secret | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
