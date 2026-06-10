# Hyperdrive endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_hyperdrive.csv

Regenerate:
```bash
python3 scripts/generate_hyperdrive_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/hyperdrive/configs` | `list-hyperdrive` | List Hyperdrives | Hyperdrive | com.cloudflare.edge.hyperdrive.database.list | cloudflare-api-tool operations hyperdrive list-hyperdrive | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/hyperdrive/configs` | `create-hyperdrive` | Create Hyperdrive | Hyperdrive | com.cloudflare.edge.hyperdrive.database.create | cloudflare-api-tool operations hyperdrive create-hyperdrive | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | DELETE | `/accounts/{account_id}/hyperdrive/configs/{hyperdrive_id}` | `delete-hyperdrive` | Delete Hyperdrive | Hyperdrive | com.cloudflare.edge.hyperdrive.database.delete | cloudflare-api-tool operations hyperdrive delete-hyperdrive | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/hyperdrive/configs/{hyperdrive_id}` | `get-hyperdrive` | Get Hyperdrive | Hyperdrive | com.cloudflare.edge.hyperdrive.database.read | cloudflare-api-tool operations hyperdrive get-hyperdrive | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PATCH | `/accounts/{account_id}/hyperdrive/configs/{hyperdrive_id}` | `patch-hyperdrive` | Patch Hyperdrive | Hyperdrive | com.cloudflare.edge.hyperdrive.database.update | cloudflare-api-tool operations hyperdrive patch-hyperdrive | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | PUT | `/accounts/{account_id}/hyperdrive/configs/{hyperdrive_id}` | `update-hyperdrive` | Update Hyperdrive | Hyperdrive | com.cloudflare.edge.hyperdrive.database.update | cloudflare-api-tool operations hyperdrive update-hyperdrive | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
