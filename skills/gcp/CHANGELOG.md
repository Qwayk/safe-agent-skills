# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- GCP source build with ADC onboarding, Discovery inventory proof files, and a source skill wrapper for `gcp`.
- Public-ready source docs for Google Cloud reads, dry-run plans, and reviewed apply gates.

### Changed
- Replaced the generic starter copy with GCP-specific README and docs that match the current runtime.
- Rewrote the GCP front-door docs again around normal customer asks, safer first reads, honest source-ready status, and clearer live-verification limits.
- Reworked the GCP first-reader docs and docs-contract tests around a clearer project-first Google Cloud review path.
- Updated the README, docs hub, and skill wrapper wording for public `gcp` install while keeping live Google Cloud account behavior marked unverified.
- Tightened the README opening and README contract test so the first screen leads with the user's cloud-admin job instead of a Google Cloud inventory list.
- Updated `.env.example`, `.env`, and onboarding output to use Google Application Default Credentials, optional quota projects, and optional allowlists.
- Regenerated the GCP boundary to include Cloud Tasks, Analytics Hub, and Data Labeling through an official googleapis proto fallback.
- Regenerated the GCP boundary to include Application Integration v1 and v2 through Google's official REST reference after the live Discovery URL returned 404.
- Tightened region allowlists so zones and common `locations/...` resource names are checked against `GCP_ALLOWED_REGIONS`.

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- The onboarding command now matches the GCP ADC runtime instead of asking for a fake base URL and token.
- Receipts now label generated writes as limited verification unless a real read-back check ran.

### Removed
- Removed the copied template guide from the source tool folder.
