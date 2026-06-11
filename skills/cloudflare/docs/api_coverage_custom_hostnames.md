# Custom Hostnames (SSL for SaaS) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): `73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824`
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_custom_hostnames.csv
- Subset intent: zone-scoped Custom Hostnames (SSL for SaaS).

Regenerate:
```bash
python3 scripts/generate_custom_hostnames_coverage.py
```

Legend:
- Implemented: command exists in this tool today
- All endpoints in this snapshot are also runnable via the advanced `cloudflare-api-tool operations <area> <op_key>` command (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/zones/{zone_id}/custom_hostnames` | `custom-hostname-for-a-zone-list-custom-hostnames` | List Custom Hostnames | Custom Hostname for a Zone | SSL and Certificates Write | SSL and Certificates Read | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-list-custom-hostnames | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/zones/{zone_id}/custom_hostnames` | `custom-hostname-for-a-zone-create-custom-hostname` | Create Custom Hostname | Custom Hostname for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-create-custom-hostname | Write-capable. Sensitive file-only output: requires --apply --yes --out. |
| Implemented | DELETE | `/zones/{zone_id}/custom_hostnames/fallback_origin` | `custom-hostname-fallback-origin-for-a-zone-delete-fallback-origin-for-custom-hostnames` | Delete Fallback Origin for Custom Hostnames | Custom Hostname Fallback Origin for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-fallback-origin-for-a-zone-delete-fallback-origin-for-custom-hostnames | Write-capable. Sensitive file-only output: requires --apply --yes --out. |
| Implemented | GET | `/zones/{zone_id}/custom_hostnames/fallback_origin` | `custom-hostname-fallback-origin-for-a-zone-get-fallback-origin-for-custom-hostnames` | Get Fallback Origin for Custom Hostnames | Custom Hostname Fallback Origin for a Zone | SSL and Certificates Write | SSL and Certificates Read | cloudflare-api-tool operations custom_hostnames custom-hostname-fallback-origin-for-a-zone-get-fallback-origin-for-custom-hostnames | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PUT | `/zones/{zone_id}/custom_hostnames/fallback_origin` | `custom-hostname-fallback-origin-for-a-zone-update-fallback-origin-for-custom-hostnames` | Update Fallback Origin for Custom Hostnames | Custom Hostname Fallback Origin for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-fallback-origin-for-a-zone-update-fallback-origin-for-custom-hostnames | Write-capable. Sensitive file-only output: requires --apply --yes --out. |
| Implemented | DELETE | `/zones/{zone_id}/custom_hostnames/{custom_hostname_id}` | `custom-hostname-for-a-zone-delete-custom-hostname-(-and-any-issued-ssl-certificates)` | Delete Custom Hostname (and any issued SSL certificates) | Custom Hostname for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-delete-custom-hostname-and-any-issued-ssl-certificates | Write-capable. Sensitive file-only output: requires --apply --yes --out. |
| Implemented | GET | `/zones/{zone_id}/custom_hostnames/{custom_hostname_id}` | `custom-hostname-for-a-zone-custom-hostname-details` | Custom Hostname Details | Custom Hostname for a Zone | SSL and Certificates Write | SSL and Certificates Read | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-custom-hostname-details | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PATCH | `/zones/{zone_id}/custom_hostnames/{custom_hostname_id}` | `custom-hostname-for-a-zone-edit-custom-hostname` | Edit Custom Hostname | Custom Hostname for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-edit-custom-hostname | Write-capable. Sensitive file-only output: requires --apply --yes --out. |
| Implemented | DELETE | `/zones/{zone_id}/custom_hostnames/{custom_hostname_id}/certificate_pack/{certificate_pack_id}/certificates/{certificate_id}` | `custom-hostname-for-a-zone-delete_single_certificate_and_key_in_a_custom_hostname` | Delete Single Certificate And Key For Custom Hostname | Custom Hostname for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-delete-single-certificate-and-key-in-a-custom-hostname | Write-capable. Sensitive file-only output: requires --apply --yes --out. |
| Implemented | PUT | `/zones/{zone_id}/custom_hostnames/{custom_hostname_id}/certificate_pack/{certificate_pack_id}/certificates/{certificate_id}` | `custom-hostname-for-a-zone-edit-custom-certificate-custom-hostname` | Replace Custom Certificate and Custom Key In Custom Hostname | Custom Hostname for a Zone | SSL and Certificates Write | cloudflare-api-tool operations custom_hostnames custom-hostname-for-a-zone-edit-custom-certificate-custom-hostname | Write-capable. Sensitive file-only output: requires --apply --yes --out. |

Totals: 10 endpoints.
