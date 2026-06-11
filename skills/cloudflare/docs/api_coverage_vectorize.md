# Vectorize (v2) (Indexes, Query/Get-by-Ids, Insert/Upsert/Delete-by-Ids, Metadata Index Ops) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_vectorize.csv

Regenerate:
```bash
python3 scripts/generate_vectorize_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/accounts/{account_id}/vectorize/v2/indexes` | `vectorize-list-vectorize-indexes` | List Vectorize Indexes | Vectorize | com.cloudflare.edge.vectorize.index.list | cloudflare-api-tool operations vectorize vectorize-list-vectorize-indexes | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes` | `vectorize-create-vectorize-index` | Create Vectorize Index | Vectorize | com.cloudflare.edge.vectorize.index.create | cloudflare-api-tool operations vectorize vectorize-create-vectorize-index | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | DELETE | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}` | `vectorize-delete-vectorize-index` | Delete Vectorize Index | Vectorize | com.cloudflare.edge.vectorize.index.delete | cloudflare-api-tool operations vectorize vectorize-delete-vectorize-index | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}` | `vectorize-get-vectorize-index` | Get Vectorize Index | Vectorize | com.cloudflare.edge.vectorize.index.read | cloudflare-api-tool operations vectorize vectorize-get-vectorize-index | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/delete_by_ids` | `vectorize-delete-vectors-by-id` | Delete Vectors By Identifier | Vectorize | com.cloudflare.edge.vectorize.index.delete | cloudflare-api-tool operations vectorize vectorize-delete-vectors-by-id | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/get_by_ids` | `vectorize-get-vectors-by-id` | Get Vectors By Identifier | Vectorize |  | cloudflare-api-tool operations vectorize vectorize-get-vectors-by-id | Read-like POST. Sensitive output: apply requires --apply and --out (no --yes); file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/info` | `vectorize-index-info` | Get Vectorize Index Info | Vectorize | com.cloudflare.edge.vectorize.index.read | cloudflare-api-tool operations vectorize vectorize-index-info | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/insert` | `vectorize-insert-vector` | Insert Vectors | Vectorize |  | cloudflare-api-tool operations vectorize vectorize-insert-vector | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/list` | `vectorize-list-vectors` | List Vectors | Vectorize | com.cloudflare.edge.vectorize.index.read | cloudflare-api-tool operations vectorize vectorize-list-vectors | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/metadata_index/create` | `vectorize-create-metadata-index` | Create Metadata Index | Vectorize | com.cloudflare.edge.vectorize.index.create | cloudflare-api-tool operations vectorize vectorize-create-metadata-index | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/metadata_index/delete` | `vectorize-delete-metadata-index` | Delete Metadata Index | Vectorize | com.cloudflare.edge.vectorize.index.delete | cloudflare-api-tool operations vectorize vectorize-delete-metadata-index | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/metadata_index/list` | `vectorize-list-metadata-indexes` | List Metadata Indexes | Vectorize |  | cloudflare-api-tool operations vectorize vectorize-list-metadata-indexes | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/query` | `vectorize-query-vector` | Query Vectors | Vectorize |  | cloudflare-api-tool operations vectorize vectorize-query-vector | Read-like POST. Sensitive output: apply requires --apply and --out (no --yes); file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/vectorize/v2/indexes/{index_name}/upsert` | `vectorize-upsert-vector` | Upsert Vectors | Vectorize |  | cloudflare-api-tool operations vectorize vectorize-upsert-vector | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
