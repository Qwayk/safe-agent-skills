# D1 endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_d1.csv

Regenerate:
```bash
python3 scripts/generate_d1_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/d1/database` | `d1-list-databases` | List D1 Databases | D1 |  | cloudflare-api-tool operations d1 d1-list-databases |  |
| Implemented | POST | `/accounts/{account_id}/d1/database` | `d1-create-database` | Create D1 Database | D1 |  | cloudflare-api-tool operations d1 d1-create-database | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | DELETE | `/accounts/{account_id}/d1/database/{database_id}` | `d1-delete-database` | Delete D1 Database | D1 |  | cloudflare-api-tool operations d1 d1-delete-database | Account write (delete). Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/d1/database/{database_id}` | `d1-get-database` | Get D1 Database | D1 |  | cloudflare-api-tool operations d1 d1-get-database |  |
| Implemented | PATCH | `/accounts/{account_id}/d1/database/{database_id}` | `d1-update-partial-database` | Update D1 Database partially | D1 |  | cloudflare-api-tool operations d1 d1-update-partial-database | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | PUT | `/accounts/{account_id}/d1/database/{database_id}` | `d1-update-database` | Update D1 Database | D1 |  | cloudflare-api-tool operations d1 d1-update-database | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | POST | `/accounts/{account_id}/d1/database/{database_id}/export` | `d1-export-database` | Export D1 Database as SQL | D1 |  | cloudflare-api-tool operations d1 d1-export-database | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/d1/database/{database_id}/import` | `d1-import-database` | Import SQL into your D1 Database | D1 |  | cloudflare-api-tool operations d1 d1-import-database | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/d1/database/{database_id}/query` | `d1-query-database` | Query D1 Database | D1 |  | cloudflare-api-tool operations d1 d1-query-database | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/d1/database/{database_id}/raw` | `d1-raw-database-query` | Raw D1 Database query | D1 |  | cloudflare-api-tool operations d1 d1-raw-database-query | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/d1/database/{database_id}/time_travel/bookmark` | `d1-time-travel-get-bookmark` | Get D1 database bookmark | D1 |  | cloudflare-api-tool operations d1 d1-time-travel-get-bookmark |  |
| Implemented | POST | `/accounts/{account_id}/d1/database/{database_id}/time_travel/restore` | `d1-time-travel-restore` | Restore D1 Database to a bookmark or point in time | D1 |  | cloudflare-api-tool operations d1 d1-time-travel-restore | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
