# Radar BGP endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_radar_bgp.csv

Regenerate:
```bash
python3 scripts/generate_radar_bgp_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/radar/bgp/hijacks/events` | `radar-get-bgp-hijacks-events` | Get BGP hijack events | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-hijacks-events |  |
| Implemented | GET | `/radar/bgp/ips/timeseries` | `radar-get-bgp-ips-timeseries` | Get announced IP address space time series | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-ips-timeseries |  |
| Implemented | GET | `/radar/bgp/leaks/events` | `radar-get-bgp-route-leak-events` | Get BGP route leak events | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-route-leak-events |  |
| Implemented | GET | `/radar/bgp/routes/ases` | `radar-get-bgp-routes-asns` | List ASes from global routing tables | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-routes-asns |  |
| Implemented | GET | `/radar/bgp/routes/moas` | `radar-get-bgp-pfx2as-moas` | Get Multi-Origin AS (MOAS) prefixes | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-pfx2as-moas |  |
| Implemented | GET | `/radar/bgp/routes/pfx2as` | `radar-get-bgp-pfx2as` | Get prefix-to-ASN mapping | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-pfx2as |  |
| Implemented | GET | `/radar/bgp/routes/realtime` | `radar-get-bgp-routes-realtime` | Get real-time BGP routes for a prefix | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-routes-realtime |  |
| Implemented | GET | `/radar/bgp/routes/stats` | `radar-get-bgp-routes-stats` | Get BGP routing table stats | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-routes-stats |  |
| Implemented | GET | `/radar/bgp/rpki/aspa/changes` | `radar-get-bgp-rpki-aspa-changes` | Get ASPA changes over time | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-rpki-aspa-changes |  |
| Implemented | GET | `/radar/bgp/rpki/aspa/snapshot` | `radar-get-bgp-rpki-aspa-snapshot` | Get ASPA objects snapshot | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-rpki-aspa-snapshot |  |
| Implemented | GET | `/radar/bgp/rpki/aspa/timeseries` | `radar-get-bgp-rpki-aspa-timeseries` | Get ASPA count time series | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-rpki-aspa-timeseries |  |
| Implemented | GET | `/radar/bgp/timeseries` | `radar-get-bgp-timeseries` | Get BGP time series | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-timeseries |  |
| Implemented | GET | `/radar/bgp/top/ases` | `radar-get-bgp-top-ases` | Get top ASes by BGP updates | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-top-ases |  |
| Implemented | GET | `/radar/bgp/top/ases/prefixes` | `radar-get-bgp-top-asns-by-prefixes` | Get top ASes by prefix count | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-top-asns-by-prefixes |  |
| Implemented | GET | `/radar/bgp/top/prefixes` | `radar-get-bgp-top-prefixes` | Get top prefixes by BGP updates | Radar BGP | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-bgp-top-prefixes |  |
