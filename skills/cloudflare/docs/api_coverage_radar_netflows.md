# Radar NetFlows endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_radar_netflows.csv

Regenerate:
```bash
python3 scripts/generate_radar_netflows_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/radar/netflows/summary` | `radar-get-netflows-summary-deprecated` | Get network traffic summary | Radar NetFlows | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-netflows-summary-deprecated |  |
| Implemented | GET | `/radar/netflows/summary/{dimension}` | `radar-get-netflows-summary` | Get network traffic distribution by dimension | Radar NetFlows | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-netflows-summary |  |
| Implemented | GET | `/radar/netflows/timeseries` | `radar-get-netflows-timeseries` | Get network traffic time series | Radar NetFlows | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-netflows-timeseries |  |
| Implemented | GET | `/radar/netflows/timeseries_groups/{dimension}` | `radar-get-netflows-timeseries-group` | Get time series distribution of network traffic by dimension | Radar NetFlows | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-netflows-timeseries-group |  |
| Implemented | GET | `/radar/netflows/top/ases` | `radar-get-netflows-top-ases` | Get top ASes by network traffic | Radar NetFlows | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-netflows-top-ases |  |
| Implemented | GET | `/radar/netflows/top/locations` | `radar-get-netflows-top-locations` | Get top locations by network traffic | Radar NetFlows | User Details Write | User Details Read | cloudflare-api-tool operations radar_all radar-get-netflows-top-locations |  |
