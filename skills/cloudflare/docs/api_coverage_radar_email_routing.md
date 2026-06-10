# Radar Email Routing endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_radar_email_routing.csv

Regenerate:
```bash
python3 scripts/generate_radar_email_routing_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/radar/email/routing/summary/arc` | `radar-get-email-routing-summary-by-arc` | Get email ARC validation summary | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary-by-arc | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/summary/dkim` | `radar-get-email-routing-summary-by-dkim` | Get email DKIM validation summary | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary-by-dkim | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/summary/dmarc` | `radar-get-email-routing-summary-by-dmarc` | Get email DMARC validation summary | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary-by-dmarc | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/summary/encrypted` | `radar-get-email-routing-summary-by-encrypted` | Get email encryption status summary | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary-by-encrypted | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/summary/ip_version` | `radar-get-email-routing-summary-by-ip-version` | Get email IP version summary | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary-by-ip-version | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/summary/spf` | `radar-get-email-routing-summary-by-spf` | Get email SPF validation summary | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary-by-spf | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/summary/{dimension}` | `radar-get-email-routing-summary` | Get email routing summary by dimension | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-summary | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/arc` | `radar-get-email-routing-timeseries-group-by-arc` | Get email ARC validation time series | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group-by-arc | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/dkim` | `radar-get-email-routing-timeseries-group-by-dkim` | Get email DKIM validation time series | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group-by-dkim | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/dmarc` | `radar-get-email-routing-timeseries-group-by-dmarc` | Get email DMARC validation time series | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group-by-dmarc | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/encrypted` | `radar-get-email-routing-timeseries-group-by-encrypted` | Get email encryption status time series | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group-by-encrypted | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/ip_version` | `radar-get-email-routing-timeseries-group-by-ip-version` | Get email IP version time series | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group-by-ip-version | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/spf` | `radar-get-email-routing-timeseries-group-by-spf` | Get email SPF validation time series | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group-by-spf | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/radar/email/routing/timeseries_groups/{dimension}` | `radar-get-email-routing-timeseries-group` | Get email routing time series grouped by dimension | Radar Email Routing |  | cloudflare-api-tool operations radar_all radar-get-email-routing-timeseries-group | Sensitive read. Requires --apply and --out; file-only output (never printed). |
