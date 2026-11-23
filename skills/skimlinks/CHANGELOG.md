# Changelog

All notable changes to this tool are documented in this file.

The tool follows SemVer. It starts at `0.1.0` because the command surface is new.

## [Unreleased]

### November 23, 2026

- Onboarding creates a private settings file even when a template is missing. A named settings file controls the account.
- Keep credentials and tokens out of request logs, errors, and returned API data. Product Key sign-in and access are reported separately.
- Show when merchant results have another page, reject invalid report rows, and require a hostname in affiliate link destinations.
- Check Product Key inputs against Skimlinks' one-search-field rule and its 100-item limit.
- Put setup and troubleshooting in one guide. Keep the real examples and dated checks.

### Fixed
- Product Key commands now require `publisher_domain_id` from `SKIMLINKS_PUBLISHER_DOMAIN_ID` or `--publisher-domain-id`, matching the official Product Key docs.
- Product Key `--sort-desc` now sends the official string values `asc` or `desc` instead of a boolean.
- The main README and first-screen docs now follow the public user-first skill-page contract instead of the older split layout.
- Public proof docs and redacted example outputs no longer leak private local workspace paths.

### Added
- Initial Skimlinks safe CLI with explicit Merchant API commands.
- Initial Reporting API commands for commission, aggregated, multi-aggregated, trending product, product bought, payment status, and deactivated merchant reports.
- Initial Product Key commands for single-product and multi-product lookups.
- Initial Link Wrapper URL builder.
- Temporary-token auth flow with Product Key credential split support.
- Redaction for token-style query parameters and audit logs.
- Coverage ledger for Merchant API, Reporting API, Product Key, Link Wrapper, Data Pipe, and Skimlinks JavaScript.
- Unit tests covering imports, auth safety, parser JSON errors, onboarding, and command-family parameter mapping.
- Manual README review for the public-facing README and quickstart opening.
- A guard test that blocks private workspace paths from reappearing in public proof docs or public example outputs.
