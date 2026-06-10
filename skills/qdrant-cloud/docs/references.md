# References (sources)

Purpose:
- Record what sources the tool relies on (auditable and reproducible).
- Prefer official provider docs and canonical operation definitions.

Rules:
- Never include secrets (API keys/tokens) in this file.
- Update “Last verified (UTC)” when re-auditing behavior or inventory.

## Official sources

- Qdrant Cloud API docs (auth + endpoints): https://qdrant.tech/documentation/cloud/cloud-api/
- Canonical operation definitions (protos + HTTP routes): https://github.com/qdrant/qdrant-cloud-public-api
  - Vendored snapshot in this tool: commit `110de0442a64b8d888c080a78569f67df7a84e94`

Last verified (UTC): 2026-03-14

