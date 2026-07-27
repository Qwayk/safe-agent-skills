# Changelog

## [Unreleased]

### Added

- Pinned Jira Cloud Platform REST API v3 and Jira Software Cloud OpenAPI inputs.
- Deterministic 721-operation inventory with fixed Platform and Software commands.
- Basic auth with Atlassian email and API token, plus OAuth 2.0 bearer support.
- Direct reads, locally signed saved write plans, full fixed-request revalidation, before-state reads where available, stronger high-risk and no-snapshot approvals, verification, and redacted receipts.
- Jira-only production target validation for Basic and OAuth credentials.
- Auditable stronger-approval categories covering 277 of 360 writes, with explicit edge-case overrides and inventory invariants.
- Explicit project-administration classification for project field-context assignment, components, versions, and version-related work.
- Wrapper checks and documentation that work in both the source layout and the published top-level `SKILL.md` layout.
- Human-first docs, safe examples, coverage ledger, tests, package checks, and tracked Jira skill wrapper.
