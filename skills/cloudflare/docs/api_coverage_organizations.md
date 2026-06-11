# Organizations (top-level) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_organizations.csv

Regenerate:
```bash
python3 scripts/generate_organizations_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/organizations` | `Organization_listOrganizations` | List organizations the user has access to | Organizations | User Details Write | User Details Read | cloudflare-api-tool operations organizations organization-listorganizations | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/organizations` | `Organizations_createUserOrganization` | Create organization | Organizations | User Details Write | cloudflare-api-tool operations organizations organizations-createuserorganization | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | DELETE | `/organizations/{organization_id}` | `Organizations_delete` | Delete organization. | Organizations |  | cloudflare-api-tool operations organizations organizations-delete | Destructive operation. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Best-effort verify. |
| Implemented | GET | `/organizations/{organization_id}` | `Organizations_retrieve` | Get organization | Organizations |  | cloudflare-api-tool operations organizations organizations-retrieve | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PUT | `/organizations/{organization_id}` | `Organizations_modify` | Modify organization. | Organizations |  | cloudflare-api-tool operations organizations organizations-modify | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/organizations/{organization_id}/accounts` | `Organizations_getAccounts` | Get organization accounts | Organizations |  | cloudflare-api-tool operations organizations organizations-getaccounts | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/organizations/{organization_id}/members` | `Members_list` | List organization members | OrganizationMembers |  | cloudflare-api-tool operations organizations members-list | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/organizations/{organization_id}/members` | `Members_create` | Create organization member | OrganizationMembers |  | cloudflare-api-tool operations organizations members-create | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | DELETE | `/organizations/{organization_id}/members/{member_id}` | `Members_delete` | Delete organization member | OrganizationMembers |  | cloudflare-api-tool operations organizations members-delete | Destructive operation. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Best-effort verify. |
| Implemented | GET | `/organizations/{organization_id}/members/{member_id}` | `Members_retrieve` | Get organization member | OrganizationMembers |  | cloudflare-api-tool operations organizations members-retrieve | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/organizations/{organization_id}/members:batchCreate` | `Members_batchCreate` | Batch create organization members | OrganizationMembers |  | cloudflare-api-tool operations organizations members-batchcreate | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/organizations/{organization_id}/profile` | `Organizations_getProfile` | Get organization profile | Organizations |  | cloudflare-api-tool operations organizations organizations-getprofile | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PUT | `/organizations/{organization_id}/profile` | `Organizations_modifyProfile` | Modify organization profile. | Organizations |  | cloudflare-api-tool operations organizations organizations-modifyprofile | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/organizations/{organization_id}/shares` | `organization-shares-list` | List organization shares | Resource Sharing |  | cloudflare-api-tool operations organizations organization-shares-list | Sensitive read. Requires --apply and --out; file-only output (never printed). |
