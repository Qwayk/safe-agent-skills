# Cache purge endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): `73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824`
- Subset intent: zone cache purge.

See the [current API coverage](api_coverage_live_official.md) for the operations available in this tool.

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | POST | `/zones/{zone_id}/purge_cache` | `zone-purge` | Purge Cached Content | Zone | Cache Purge | cloudflare-api-tool operations cache_purge zone-purge | Write-capable. Dry-run by default; apply requires --apply --yes. Requires --body-json-file. |

Totals: 1 endpoints.
