# DLP Email (scanner rules) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_dlp_email.csv

Regenerate:
```bash
python3 scripts/generate_dlp_email_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/dlp/email/account_mapping` | `dlp-email-scanner-get-account-mapping` | Get mapping | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-get-account-mapping | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/dlp/email/account_mapping` | `dlp-email-scanner-create-account-mapping` | Create mapping | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-create-account-mapping | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/dlp/email/rules` | `dlp-email-scanner-list-all-rules` | List all email scanner rules | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-list-all-rules | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PATCH | `/accounts/{account_id}/dlp/email/rules` | `dlp-email-scanner-update-rule-priorities` | Update email scanner rule priorities | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-update-rule-priorities | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/dlp/email/rules` | `dlp-email-scanner-create-rule` | Create email scanner rule | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-create-rule | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | DELETE | `/accounts/{account_id}/dlp/email/rules/{rule_id}` | `dlp-email-scanner-delete-rule` | Delete email scanner rule | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-delete-rule | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/dlp/email/rules/{rule_id}` | `dlp-email-scanner-get-rule` | Get an email scanner rule | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-get-rule | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PUT | `/accounts/{account_id}/dlp/email/rules/{rule_id}` | `dlp-email-scanner-update-rule` | Update email scanner rule | DLP Email |  | cloudflare-api-tool operations dlp_email dlp-email-scanner-update-rule | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
