# Changelog

All notable source changes are recorded here. This project uses Semantic Versioning; pre-1.0 minor releases may include breaking changes.

## [Unreleased]

### Added

- Initial Xero safe-agent CLI.
- Deterministic inventory for Xero OpenAPI release 16.1.0 at commit `e952d0bda3628facbf7afc5990ad6a0e7e77bd1e`.
- 474 fixed commands covering the pinned OpenAPI boundary and the documented eInvoicing supplement.
- OAuth 2.0 PKCE, paid single-organisation Custom Connection, and non-tenanted App Store auth paths.
- Exact tenant selection, protected reads, plan-first writes, extra high-risk approval, verification, and receipts.
- Pinned catalog integrity, recursive fixed-contract validation, all-value masking for sensitive output, one-use plan reservations, and current official access and region classifications.

### Changed

- Classified all four Xero App Store subscription commands as deprecated legacy XASS transition access, with the 4 December 2025 new-app cutoff, 1 July 2026 customer-migration deadline, and live-entitlement limit recorded consistently in generated metadata, coverage, docs, tests, and the wrapper.
