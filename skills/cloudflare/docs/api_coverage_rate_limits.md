# Rate limits (WAF) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_rate_limits.csv

Regenerate:
```bash
python3 scripts/generate_rate_limits_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/zones/{zone_id}/rate_limits` | `rate-limits-for-a-zone-list-rate-limits` | List rate limits | Rate limits for a zone |  | cloudflare-api-tool operations rate_limits rate-limits-for-a-zone-list-rate-limits |  |
| Implemented | POST | `/zones/{zone_id}/rate_limits` | `rate-limits-for-a-zone-create-a-rate-limit` | Create a rate limit | Rate limits for a zone |  | cloudflare-api-tool operations rate_limits rate-limits-for-a-zone-create-a-rate-limit | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | DELETE | `/zones/{zone_id}/rate_limits/{rate_limit_id}` | `rate-limits-for-a-zone-delete-a-rate-limit` | Delete a rate limit | Rate limits for a zone |  | cloudflare-api-tool operations rate_limits rate-limits-for-a-zone-delete-a-rate-limit | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/rate_limits/{rate_limit_id}` | `rate-limits-for-a-zone-get-a-rate-limit` | Get a rate limit | Rate limits for a zone |  | cloudflare-api-tool operations rate_limits rate-limits-for-a-zone-get-a-rate-limit |  |
| Implemented | PUT | `/zones/{zone_id}/rate_limits/{rate_limit_id}` | `rate-limits-for-a-zone-update-a-rate-limit` | Update a rate limit | Rate limits for a zone |  | cloudflare-api-tool operations rate_limits rate-limits-for-a-zone-update-a-rate-limit | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
