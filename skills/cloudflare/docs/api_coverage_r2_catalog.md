# R2 Catalog endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_r2_catalog.csv

Regenerate:
```bash
python3 scripts/generate_r2_catalog_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/r2-catalog` | `list-catalogs` | List R2 catalogs | R2 Catalog Management |  | cloudflare-api-tool operations r2_catalog list-catalogs |  |
| Implemented | GET | `/accounts/{account_id}/r2-catalog/{bucket_name}` | `get-catalog-details` | Get R2 catalog details | R2 Catalog Management |  | cloudflare-api-tool operations r2_catalog get-catalog-details |  |
| Implemented | POST | `/accounts/{account_id}/r2-catalog/{bucket_name}/credential` | `store-credentials` | Store catalog credentials | Credential Management |  | cloudflare-api-tool operations r2_catalog store-credentials | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/r2-catalog/{bucket_name}/disable` | `disable-catalog` | Disable R2 catalog | R2 Catalog Management |  | cloudflare-api-tool operations r2_catalog disable-catalog | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | POST | `/accounts/{account_id}/r2-catalog/{bucket_name}/enable` | `enable-catalog` | Enable R2 bucket as a catalog | R2 Catalog Management |  | cloudflare-api-tool operations r2_catalog enable-catalog | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/r2-catalog/{bucket_name}/maintenance-configs` | `get-maintenance-config` | Get catalog maintenance configuration | Maintenance Configuration |  | cloudflare-api-tool operations r2_catalog get-maintenance-config |  |
| Implemented | POST | `/accounts/{account_id}/r2-catalog/{bucket_name}/maintenance-configs` | `update-maintenance-config` | Update catalog maintenance configuration | Maintenance Configuration |  | cloudflare-api-tool operations r2_catalog update-maintenance-config | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/r2-catalog/{bucket_name}/namespaces` | `list-namespaces` | List namespaces in catalog | Namespace Management |  | cloudflare-api-tool operations r2_catalog list-namespaces |  |
| Implemented | GET | `/accounts/{account_id}/r2-catalog/{bucket_name}/namespaces/{namespace}/tables` | `list-tables` | List tables in namespace | Table Management |  | cloudflare-api-tool operations r2_catalog list-tables |  |
| Implemented | GET | `/accounts/{account_id}/r2-catalog/{bucket_name}/namespaces/{namespace}/tables/{table_name}/maintenance-configs` | `get-table-maintenance-config` | Get table maintenance configuration | Table Maintenance Configuration |  | cloudflare-api-tool operations r2_catalog get-table-maintenance-config |  |
| Implemented | POST | `/accounts/{account_id}/r2-catalog/{bucket_name}/namespaces/{namespace}/tables/{table_name}/maintenance-configs` | `update-table-maintenance-config` | Update table maintenance configuration | Table Maintenance Configuration |  | cloudflare-api-tool operations r2_catalog update-table-maintenance-config | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
