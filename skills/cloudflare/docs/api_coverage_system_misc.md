# System / misc (top-level) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 0dbf95a292b802ba95622a31fe82e0a069c53c0cddeaf9d3ccbc9d2ac9918aff
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_system_misc.csv

Regenerate:
```bash
python3 scripts/generate_system_misc_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations system_misc <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts` | `accounts-list-accounts` | List Accounts | Accounts |  | cloudflare-api-tool operations system_misc accounts-list-accounts |  |
| Implemented | GET | `/certificates` | `origin-ca-list-certificates` | List Certificates | Origin CA |  | cloudflare-api-tool operations system_misc origin-ca-list-certificates | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/certificates` | `origin-ca-create-certificate` | Create Certificate | Origin CA |  | cloudflare-api-tool operations system_misc origin-ca-create-certificate | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | DELETE | `/certificates/{certificate_id}` | `origin-ca-revoke-certificate` | Revoke Certificate | Origin CA |  | cloudflare-api-tool operations system_misc origin-ca-revoke-certificate | Destructive operation. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Best-effort verify. |
| Implemented | GET | `/certificates/{certificate_id}` | `origin-ca-get-certificate` | Get Certificate | Origin CA |  | cloudflare-api-tool operations system_misc origin-ca-get-certificate | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/internal/submit` |  | Internal route for testing URL submissions | brand_protection |  | cloudflare-api-tool operations system_misc post-internal-submit | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/ips` | `cloudflare-ips-cloudflare-ip-details` | Cloudflare/JD Cloud IP Details | Cloudflare IPs |  | cloudflare-api-tool operations system_misc cloudflare-ips-cloudflare-ip-details |  |
| Implemented | GET | `/live` |  | Run liveness checks | brand_protection |  | cloudflare-api-tool operations system_misc get-live |  |
| Implemented | GET | `/ready` |  | Run readiness checks | brand_protection |  | cloudflare-api-tool operations system_misc get-ready |  |
| Implemented | GET | `/signed-url` |  | Internal route for testing signed URLs | logo_match |  | cloudflare-api-tool operations system_misc get-signed-url | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/system/accounts/{account_tag}/stores` | `secrets-store-system-list` | List account stores (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-list | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/system/accounts/{account_tag}/stores` | `secrets-store-system-create` | Create a store (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-create | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | DELETE | `/system/accounts/{account_tag}/stores/{store_id}` | `secrets-store-system-delete-by-id` | Delete a store (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-delete-by-id | Destructive operation. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Best-effort verify. |
| Implemented | GET | `/system/accounts/{account_tag}/stores/{store_id}` | `secrets-store-system-get-store-by-id` | Get a store by ID (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-get-store-by-id | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | DELETE | `/system/accounts/{account_tag}/stores/{store_id}/secrets` | `secrets-store-system-delete-bulk` | Delete secrets (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-delete-bulk | Destructive operation. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Best-effort verify. |
| Implemented | GET | `/system/accounts/{account_tag}/stores/{store_id}/secrets` | `secrets-store-system-secrets-list` | List store secrets (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-secrets-list | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/system/accounts/{account_tag}/stores/{store_id}/secrets` | `secrets-store-system-secret-create` | Create secrets (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-secret-create | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | DELETE | `/system/accounts/{account_tag}/stores/{store_id}/secrets/{secret_id}` | `secrets-store-system-secret-delete-by-id` | Delete a secret (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-secret-delete-by-id | Destructive operation. Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Best-effort verify. |
| Implemented | GET | `/system/accounts/{account_tag}/stores/{store_id}/secrets/{secret_id}` | `secrets-store-system-get-by-id` | Get a secret by ID (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-get-by-id | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PATCH | `/system/accounts/{account_tag}/stores/{store_id}/secrets/{secret_id}` | `secrets-store-system-patch-by-id` | Patch a secret (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-patch-by-id | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | POST | `/system/accounts/{account_tag}/stores/{store_id}/secrets/{secret_id}/duplicate` | `secrets-store-system-duplicate-by-id` | Duplicate secret (System) | Secrets Store |  | cloudflare-api-tool operations system_misc secrets-store-system-duplicate-by-id | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | GET | `/zones` | `zones-get` | List Zones | Zone | Zone Zone Read | cloudflare-api-tool operations system_misc zones-get |  |
| Implemented | POST | `/zones` | `zones-post` | Create Zone | Zone | Zone Zone Edit \| Zone DNS Edit | cloudflare-api-tool operations system_misc zones-post | Implemented via allowlisted operations command (plan by default; apply requires --apply --yes; best-effort verify). |
