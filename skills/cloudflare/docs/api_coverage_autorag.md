# AutoRAG (RAG search + files/jobs + job logs) (Phase 13) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_autorag.csv

Regenerate:
```bash
python3 scripts/generate_autorag_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | POST | `/accounts/{account_id}/autorag/rags/{id}/ai-search` | `autorag-config-ai-search` | AI Search | AutoRAG RAG Search | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-ai-search | Read-like POST. Sensitive output: apply requires --apply and --out (no --yes); file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/autorag/rags/{id}/files` | `autorag-config-files` | Files | AutoRAG RAG | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-files | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/autorag/rags/{id}/jobs` | `autorag-config-list-jobs` | List Jobs | AutoRAG Jobs | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-list-jobs | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/autorag/rags/{id}/jobs/{job_id}` | `autorag-config-get-job` | Get a Job Details | AutoRAG Jobs | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-get-job | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | GET | `/accounts/{account_id}/autorag/rags/{id}/jobs/{job_id}/logs` | `autorag-config-list-job-logs` | List Job Logs | AutoRAG Jobs | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-list-job-logs | Sensitive read. Requires --apply and --out; file-only output (never printed). |
| Implemented | POST | `/accounts/{account_id}/autorag/rags/{id}/search` | `autorag-config-search` | Search | AutoRAG RAG Search | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-search | Read-like POST. Sensitive output: apply requires --apply and --out (no --yes); file-only output (never printed). |
| Implemented | PATCH | `/accounts/{account_id}/autorag/rags/{id}/sync` | `autorag-config-sync` | Sync | AutoRAG RAG | com.cloudflare.api.account.rag | cloudflare-api-tool operations autorag autorag-config-sync | Sensitive output. Apply requires --apply --yes and --out; file-only output (never printed). |
