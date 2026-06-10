# Registrar domains endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_registrar.csv

Regenerate:
```bash
python3 scripts/generate_registrar_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/registrar/domains` | `registrar-domains-list-domains` | List domains | Registrar Domains |  | cloudflare-api-tool operations registrar registrar-domains-list-domains | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/registrar/domains/{domain_name}` | `registrar-domains-get-domain` | Get domain | Registrar Domains |  | cloudflare-api-tool operations registrar registrar-domains-get-domain | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | PUT | `/accounts/{account_id}/registrar/domains/{domain_name}` | `registrar-domains-update-domain` | Update domain | Registrar Domains |  | cloudflare-api-tool operations registrar registrar-domains-update-domain | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
