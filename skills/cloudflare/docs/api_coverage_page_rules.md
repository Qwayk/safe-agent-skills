# Page rules (WAF) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_page_rules.csv

Regenerate:
```bash
python3 scripts/generate_page_rules_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/zones/{zone_id}/pagerules` | `page-rules-list-page-rules` | List Page Rules | Page Rules |  | cloudflare-api-tool operations page_rules page-rules-list-page-rules |  |
| Implemented | POST | `/zones/{zone_id}/pagerules` | `page-rules-create-a-page-rule` | Create a Page Rule | Page Rules |  | cloudflare-api-tool operations page_rules page-rules-create-a-page-rule | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/pagerules/settings` | `available-page-rules-settings-list-available-page-rules-settings` | List available Page Rules settings | Available Page Rules settings |  | cloudflare-api-tool operations page_rules available-page-rules-settings-list-available-page-rules-settings |  |
| Implemented | DELETE | `/zones/{zone_id}/pagerules/{pagerule_id}` | `page-rules-delete-a-page-rule` | Delete a Page Rule | Page Rules |  | cloudflare-api-tool operations page_rules page-rules-delete-a-page-rule | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/pagerules/{pagerule_id}` | `page-rules-get-a-page-rule` | Get a Page Rule | Page Rules |  | cloudflare-api-tool operations page_rules page-rules-get-a-page-rule |  |
| Implemented | PATCH | `/zones/{zone_id}/pagerules/{pagerule_id}` | `page-rules-edit-a-page-rule` | Edit a Page Rule | Page Rules |  | cloudflare-api-tool operations page_rules page-rules-edit-a-page-rule | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | PUT | `/zones/{zone_id}/pagerules/{pagerule_id}` | `page-rules-update-a-page-rule` | Update a Page Rule | Page Rules |  | cloudflare-api-tool operations page_rules page-rules-update-a-page-rule | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
