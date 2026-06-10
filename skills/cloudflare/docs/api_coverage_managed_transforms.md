# Managed Transforms (WAF) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_managed_transforms.csv

Regenerate:
```bash
python3 scripts/generate_managed_transforms_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | DELETE | `/zones/{zone_id}/managed_headers` | `deleteManagedTransforms` | Delete Managed Transforms | Managed Transforms |  | cloudflare-api-tool operations managed_transforms deletemanagedtransforms | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/managed_headers` | `listManagedTransforms` | List Managed Transforms | Managed Transforms |  | cloudflare-api-tool operations managed_transforms listmanagedtransforms |  |
| Implemented | PATCH | `/zones/{zone_id}/managed_headers` | `updateManagedTransforms` | Update Managed Transforms | Managed Transforms |  | cloudflare-api-tool operations managed_transforms updatemanagedtransforms | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
