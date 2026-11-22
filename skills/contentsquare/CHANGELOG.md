# Changelog

## November 22, 2026

- Setup keeps the chosen settings file and creates new files with owner-only access. Source archives include the skill, guides and settings example.
- Applying a change checks the saved action, request and Contentsquare connection. Make a fresh preview for an older plan. The CLI sends each approved change once.
- Receipts show whether Contentsquare accepted a request, rejected it or left the result uncertain. Export replies show the run state and where to check for files. Download checks protect an existing file from an empty or incomplete replacement.
- The setup, command and approval guides now hold the instructions that were spread across several pages.

## [0.1.0] - 2026-06-25

### Added

- Initial Contentsquare API skill for Data Export, Metrics, Enrichment, and Speed Analysis Lab.
- Server-to-server OAuth configuration and redacted auth checks.
- Explicit named commands for the official server-side REST endpoint surface.
- Dry-run, reviewed apply, plan, and receipt flow for write operations.
- Public-ready README, docs, coverage ledger, examples, proof notes, and skill wrapper.

### Fixed

- Repaired read command query parameters so the API request uses official Contentsquare names such as `projectId`, `startDate`, `endDate`, `segmentIds`, `goalId`, `period`, `ids`, `state`, `order`, `format`, `frequency`, `scope`, `from`, and `to`.
- Repaired `data-export download-run-file` so it uses documented nested `files[].url` values and refuses to guess when a run has multiple files; users can choose by `--file-index` or `--part-id`.
- Repaired OAuth request bodies so token requests use official family scopes, account-level credentials can send `project_id`, and `auth me` sends the documented `client_id` / `client_secret` body.
