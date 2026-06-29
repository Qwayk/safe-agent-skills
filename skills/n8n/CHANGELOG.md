# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Initial n8n source tool.
- Pinned the official n8n public API spec folder from `n8n-io/n8n` commit `0c92df794a07404d22cbc85a3c4ed6b332e442ab`.
- Generated an 80-operation inventory across 15 official public REST API families.
- Added explicit generated commands under `api <family> <command>`.
- Added API-key auth with `X-N8N-API-KEY`.
- Added review-first write plans, plan matching, no-snapshot approval, high-risk approval, receipts, run history, and redaction.
- Added n8n-specific README, docs, proof notes, coverage, and skill wrapper.
- Added focused regression coverage for command-string redaction, HTTP failure redaction, and HTTP error-body secret-key redaction.
