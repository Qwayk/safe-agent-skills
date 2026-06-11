# Cloudflare Images (Images, Variants, Signing Keys) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_images.csv

Regenerate:
```bash
python3 scripts/generate_images_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/images/v1` | `cloudflare-images-list-images` | List images | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-list-images |  |
| Implemented | POST | `/accounts/{account_id}/images/v1` | `cloudflare-images-upload-an-image-via-url` | Upload an image | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-upload-an-image-via-url | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/images/v1/keys` | `cloudflare-images-keys-list-signing-keys` | List Signing Keys | Cloudflare Images Keys |  | cloudflare-api-tool operations images cloudflare-images-keys-list-signing-keys | Signing keys can return key material. Apply requires --apply --ack-irreversible and --out; file-only output (never printed). |
| Implemented | DELETE | `/accounts/{account_id}/images/v1/keys/{signing_key_name}` | `cloudflare-images-keys-delete-signing-key` | Delete Signing Key | Cloudflare Images Keys |  | cloudflare-api-tool operations images cloudflare-images-keys-delete-signing-key | Signing keys can return key material. Apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | PUT | `/accounts/{account_id}/images/v1/keys/{signing_key_name}` | `cloudflare-images-keys-add-signing-key` | Create a new Signing Key | Cloudflare Images Keys |  | cloudflare-api-tool operations images cloudflare-images-keys-add-signing-key | Signing keys can return key material. Apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/images/v1/stats` | `cloudflare-images-images-usage-statistics` | Images usage statistics | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-images-usage-statistics |  |
| Implemented | GET | `/accounts/{account_id}/images/v1/variants` | `cloudflare-images-variants-list-variants` | List variants | Cloudflare Images Variants |  | cloudflare-api-tool operations images cloudflare-images-variants-list-variants |  |
| Implemented | POST | `/accounts/{account_id}/images/v1/variants` | `cloudflare-images-variants-create-a-variant` | Create a variant | Cloudflare Images Variants |  | cloudflare-api-tool operations images cloudflare-images-variants-create-a-variant | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | DELETE | `/accounts/{account_id}/images/v1/variants/{variant_id}` | `cloudflare-images-variants-delete-a-variant` | Delete a variant | Cloudflare Images Variants |  | cloudflare-api-tool operations images cloudflare-images-variants-delete-a-variant | Account write (delete). Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/images/v1/variants/{variant_id}` | `cloudflare-images-variants-variant-details` | Variant details | Cloudflare Images Variants |  | cloudflare-api-tool operations images cloudflare-images-variants-variant-details |  |
| Implemented | PATCH | `/accounts/{account_id}/images/v1/variants/{variant_id}` | `cloudflare-images-variants-update-a-variant` | Update a variant | Cloudflare Images Variants |  | cloudflare-api-tool operations images cloudflare-images-variants-update-a-variant | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | DELETE | `/accounts/{account_id}/images/v1/{image_id}` | `cloudflare-images-delete-image` | Delete image | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-delete-image | Account write (delete). Dry-run plan by default; apply requires --apply --yes --ack-irreversible and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/images/v1/{image_id}` | `cloudflare-images-image-details` | Image details | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-image-details |  |
| Implemented | PATCH | `/accounts/{account_id}/images/v1/{image_id}` | `cloudflare-images-update-image` | Update image | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-update-image | Account write. Dry-run plan by default; apply requires --apply --yes and --out; file-only output (never printed). Receipts are redacted; best-effort verify. |
| Implemented | GET | `/accounts/{account_id}/images/v1/{image_id}/blob` | `cloudflare-images-base-image` | Base image | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-base-image | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/images/v2` | `cloudflare-images-list-images-v2` | List images V2 | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-list-images-v2 |  |
| Implemented | POST | `/accounts/{account_id}/images/v2/direct_upload` | `cloudflare-images-create-authenticated-direct-upload-url-v-2` | Create authenticated direct upload URL V2 | Cloudflare Images |  | cloudflare-api-tool operations images cloudflare-images-create-authenticated-direct-upload-url-v-2 | Read-like POST. Sensitive output: apply requires --apply and --out (no --yes); file-only output (never printed). |
