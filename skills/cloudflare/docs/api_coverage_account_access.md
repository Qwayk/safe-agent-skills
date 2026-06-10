# Account access endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_all.csv

Regenerate:
```bash
python3 scripts/generate_account_access_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/members` | `account-members-list-members` | List Members | Account Members | #organization:read | cloudflare-api-tool operations account_access account-members-list-members | PII-safe: output is file-only (never printed). Requires --apply and --out. |
| Implemented | POST | `/accounts/{account_id}/members` | `account-members-add-member` | Add Member | Account Members | #organization:edit | cloudflare-api-tool operations account_access account-members-add-member | PII-safe write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; never prints emails. |
| Implemented | DELETE | `/accounts/{account_id}/members/{member_id}` | `account-members-remove-member` | Remove Member | Account Members | #organization:edit | cloudflare-api-tool operations account_access account-members-remove-member | PII-safe delete. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; never prints emails. |
| Implemented | GET | `/accounts/{account_id}/members/{member_id}` | `account-members-member-details` | Member Details | Account Members | #organization:read | cloudflare-api-tool operations account_access account-members-member-details | PII-safe: output is file-only (never printed). Requires --apply and --out. |
| Implemented | PUT | `/accounts/{account_id}/members/{member_id}` | `account-members-update-member` | Update Member | Account Members | #organization:edit | cloudflare-api-tool operations account_access account-members-update-member | PII-safe write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; never prints emails. |
| Implemented | GET | `/accounts/{account_id}/roles` | `account-roles-list-roles` | List Roles | Account Roles | #organization:read | cloudflare-api-tool operations account_access account-roles-list-roles |  |
| Implemented | GET | `/accounts/{account_id}/roles/{role_id}` | `account-roles-role-details` | Role Details | Account Roles | #organization:read | cloudflare-api-tool operations account_access account-roles-role-details |  |
