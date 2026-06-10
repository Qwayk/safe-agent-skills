# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial PayPal REST API tool with 133 explicit commands across orders, payments, vault, invoicing, webhooks, subscriptions, disputes, payouts, partner, tracking, reporting, and identity surfaces.
- PayPal OAuth client-credentials auth flow, onboarding, run-history artifacts, proof docs, and skill wrapper.
- Write plans now include `before_state` and an explicit no-snapshot approval verification plan.

### Changed
- Replaced the starter auth assumptions with PayPal client ID and client secret setup.
- Marked query-style `POST` endpoints as read-only where PayPal documents them as lookup or verification flows.
- Rewrote the customer docs to match the shipped PayPal command surface.
- Write apply requires explicit no-snapshot approval when command-specific before-state support is unavailable; missing approval refuses before PayPal auth or HTTP.

### Fixed
- `auth check` now returns a redacted `ToolError` on auth failure.
- PayPal coverage docs stay aligned with the shipped operation catalog through tests.

### Removed
- Public docs for unshipped scaffold-only jobs, demo, and manual-token helper commands.
