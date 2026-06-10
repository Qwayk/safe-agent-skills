# Email Security (Investigate, Submissions, PhishGuard) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_email_security.csv

Regenerate:
```bash
python3 scripts/generate_email_security_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/email-security/investigate` | `email_security_investigate` | Search email messages | Email Security |  | cloudflare-api-tool operations email_security email-security-investigate | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/email-security/investigate/move` | `email_security_post_bulk_message_move` | Move multiple messages | Email Security |  | cloudflare-api-tool operations email_security email-security-post-bulk-message-move | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/email-security/investigate/preview` | `email_security_post_preview` | Preview for non-detection messages | Email Security |  | cloudflare-api-tool operations email_security email-security-post-preview | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/email-security/investigate/release` | `email_security_post_release` | Release messages from quarantine | Email Security |  | cloudflare-api-tool operations email_security email-security-post-release | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/investigate/{postfix_id}` | `email_security_get_message` | Get message details | Email Security |  | cloudflare-api-tool operations email_security email-security-get-message | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/investigate/{postfix_id}/detections` | `email_security_get_message_detections` | Get message detection details | Email Security |  | cloudflare-api-tool operations email_security email-security-get-message-detections | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/email-security/investigate/{postfix_id}/move` | `email_security_post_message_move` | Move a message | Email Security |  | cloudflare-api-tool operations email_security email-security-post-message-move | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/investigate/{postfix_id}/preview` | `email_security_get_message_preview` | Get email preview | Email Security |  | cloudflare-api-tool operations email_security email-security-get-message-preview | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/investigate/{postfix_id}/raw` | `email_security_get_message_raw` | Get raw email content | Email Security |  | cloudflare-api-tool operations email_security email-security-get-message-raw | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/email-security/investigate/{postfix_id}/reclassify` | `email_security_post_reclassify` | Change email classfication | Email Security |  | cloudflare-api-tool operations email_security email-security-post-reclassify | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/investigate/{postfix_id}/trace` | `email_security_get_message_trace` | Get email trace | Email Security |  | cloudflare-api-tool operations email_security email-security-get-message-trace | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/phishguard/reports` | `email_security_get_phishguard_reports` | Get `PhishGuard` reports | Email Security |  | cloudflare-api-tool operations email_security email-security-get-phishguard-reports | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/email-security/submissions` | `email_security_submissions` | Get reclassify submissions | Email Security |  | cloudflare-api-tool operations email_security email-security-submissions | Sensitive read. Requires --apply and --out; file-only output (never printed). |
