# Filters (WAF) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_filters.csv

Regenerate:
```bash
python3 scripts/generate_filters_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | DELETE | `/zones/{zone_id}/filters` | `filters-delete-filters` | Delete filters | Filters |  | cloudflare-api-tool operations filters filters-delete-filters | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/filters` | `filters-list-filters` | List filters | Filters |  | cloudflare-api-tool operations filters filters-list-filters |  |
| Implemented | POST | `/zones/{zone_id}/filters` | `filters-create-filters` | Create filters | Filters |  | cloudflare-api-tool operations filters filters-create-filters | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | PUT | `/zones/{zone_id}/filters` | `filters-update-filters` | Update filters | Filters |  | cloudflare-api-tool operations filters filters-update-filters | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | DELETE | `/zones/{zone_id}/filters/{filter_id}` | `filters-delete-a-filter` | Delete a filter | Filters |  | cloudflare-api-tool operations filters filters-delete-a-filter | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/filters/{filter_id}` | `filters-get-a-filter` | Get a filter | Filters |  | cloudflare-api-tool operations filters filters-get-a-filter |  |
| Implemented | PUT | `/zones/{zone_id}/filters/{filter_id}` | `filters-update-a-filter` | Update a filter | Filters |  | cloudflare-api-tool operations filters filters-update-a-filter | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
