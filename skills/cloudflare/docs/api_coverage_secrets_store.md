# Secrets Store endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_secrets_store.csv

Regenerate:
```bash
python3 scripts/generate_secrets_store_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/secrets_store/quota` | `secrets-store-quota` | View secret usage | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-quota |  |
| Implemented | GET | `/accounts/{account_id}/secrets_store/stores` | `secrets-store-list` | List account stores | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.list | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-list |  |
| Implemented | POST | `/accounts/{account_id}/secrets_store/stores` | `secrets-store-create` | Create a store | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | #com.cloudflare.api.account.secrets-store.secret.create | cloudflare-api-tool operations secrets_store secrets-store-create | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | DELETE | `/accounts/{account_id}/secrets_store/stores/{store_id}` | `secrets-store-delete-by-id` | Delete a store | Secrets Store |  | cloudflare-api-tool operations secrets_store secrets-store-delete-by-id | Account write (delete). Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | DELETE | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets` | `secrets-store-delete-bulk` | Delete secrets | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | #com.cloudflare.api.account.secrets-store.secret.delete | cloudflare-api-tool operations secrets_store secrets-store-delete-bulk | Account write (delete). Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets` | `secrets-store-secrets-list` | List store secrets | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.list | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-secrets-list |  |
| Implemented | POST | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets` | `secrets-store-secret-create` | Create a secret | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | #com.cloudflare.api.account.secrets-store.secret.create | cloudflare-api-tool operations secrets_store secrets-store-secret-create | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | DELETE | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}` | `secrets-store-secret-delete-by-id` | Delete a secret | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-secret-delete-by-id | Account write (delete). Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}` | `secrets-store-get-by-id` | Get a secret by ID | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-get-by-id | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PATCH | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}` | `secrets-store-patch-by-id` | Patch a secret | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-patch-by-id | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}/duplicate` | `secrets-store-duplicate-by-id` | Duplicate Secret | Secrets Store | #com.cloudflare.api.account.secrets-store.secret.read | cloudflare-api-tool operations secrets_store secrets-store-duplicate-by-id | Secret-bearing write result. Requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
