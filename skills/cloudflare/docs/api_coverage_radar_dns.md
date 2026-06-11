# Radar DNS endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_radar_dns.csv

Regenerate:
```bash
python3 scripts/generate_radar_dns_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/radar/dns/summary/cache_hit` | `radar-get-dns-summary-by-cache-hit-status` | Get DNS queries by cache status summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-cache-hit-status |  |
| Implemented | GET | `/radar/dns/summary/dnssec` | `radar-get-dns-summary-by-dnssec` | Get DNS queries by DNSSEC support summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-dnssec |  |
| Implemented | GET | `/radar/dns/summary/dnssec_aware` | `radar-get-dns-summary-by-dnssec-awareness` | Get DNS queries by DNSSEC awareness summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-dnssec-awareness |  |
| Implemented | GET | `/radar/dns/summary/dnssec_e2e` | `radar-get-dns-summary-by-dnssec-e2e-version` | Get DNS queries by DNSSEC end-to-end summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-dnssec-e2e-version |  |
| Implemented | GET | `/radar/dns/summary/ip_version` | `radar-get-dns-summary-by-ip-version` | Get DNS queries by IP version summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-ip-version |  |
| Implemented | GET | `/radar/dns/summary/matching_answer` | `radar-get-dns-summary-by-matching-answer-status` | Get DNS queries by matching answer summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-matching-answer-status |  |
| Implemented | GET | `/radar/dns/summary/protocol` | `radar-get-dns-summary-by-protocol` | Get DNS queries by protocol summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-protocol |  |
| Implemented | GET | `/radar/dns/summary/query_type` | `radar-get-dns-summary-by-query-type` | Get DNS queries by type summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-query-type |  |
| Implemented | GET | `/radar/dns/summary/response_code` | `radar-get-dns-summary-by-response-code` | Get DNS queries by response code summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-response-code |  |
| Implemented | GET | `/radar/dns/summary/response_ttl` | `radar-get-dns-summary-by-response-ttl` | Get DNS queries by response TTL summary | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary-by-response-ttl |  |
| Implemented | GET | `/radar/dns/summary/{dimension}` | `radar-get-dns-summary` | Get DNS summary by dimension | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-summary |  |
| Implemented | GET | `/radar/dns/timeseries` | `radar-get-dns-timeseries` | Get DNS queries time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries |  |
| Implemented | GET | `/radar/dns/timeseries_groups/cache_hit` | `radar-get-dns-timeseries-group-by-cache-hit-status` | Get DNS queries by cache status time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-cache-hit-status |  |
| Implemented | GET | `/radar/dns/timeseries_groups/dnssec` | `radar-get-dns-timeseries-group-by-dnssec` | Get DNS queries by DNSSEC support time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-dnssec |  |
| Implemented | GET | `/radar/dns/timeseries_groups/dnssec_aware` | `radar-get-dns-timeseries-group-by-dnssec-awareness` | Get DNS queries by DNSSEC awareness time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-dnssec-awareness |  |
| Implemented | GET | `/radar/dns/timeseries_groups/dnssec_e2e` | `radar-get-dns-timeseries-group-by-dnssec-e2e-version` | Get DNS queries by DNSSEC end-to-end time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-dnssec-e2e-version |  |
| Implemented | GET | `/radar/dns/timeseries_groups/ip_version` | `radar-get-dns-timeseries-group-by-ip-version` | Get DNS queries by IP version time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-ip-version |  |
| Implemented | GET | `/radar/dns/timeseries_groups/matching_answer` | `radar-get-dns-timeseries-group-by-matching-answer-status` | Get DNS queries by matching answer time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-matching-answer-status |  |
| Implemented | GET | `/radar/dns/timeseries_groups/protocol` | `radar-get-dns-timeseries-group-by-protocol` | Get DNS queries by protocol time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-protocol |  |
| Implemented | GET | `/radar/dns/timeseries_groups/query_type` | `radar-get-dns-timeseries-group-by-query-type` | Get DNS queries by type time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-query-type |  |
| Implemented | GET | `/radar/dns/timeseries_groups/response_code` | `radar-get-dns-timeseries-group-by-response-code` | Get DNS queries by response code time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-response-code |  |
| Implemented | GET | `/radar/dns/timeseries_groups/response_ttl` | `radar-get-dns-timeseries-group-by-response-ttl` | Get DNS queries by response TTL time series | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group-by-response-ttl |  |
| Implemented | GET | `/radar/dns/timeseries_groups/{dimension}` | `radar-get-dns-timeseries-group` | Get DNS time series grouped by dimension | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-timeseries-group |  |
| Implemented | GET | `/radar/dns/top/ases` | `radar-get-dns-top-ases` | Get top ASes by DNS queries | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-top-ases |  |
| Implemented | GET | `/radar/dns/top/locations` | `radar-get-dns-top-locations` | Get top locations by DNS queries | Radar DNS | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-dns-top-locations |  |
