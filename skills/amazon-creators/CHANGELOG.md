## Unreleased

- Fixed live catalog requests to expand the CLI's high-level resource aliases into Amazon's official operation-specific resource enums, corrected the default `search` preset to `search-lens`, and updated the tests/docs so real authenticated catalog calls work.
- Added an inventory test that locks the Issue #404 scope to the four public catalog operations plus the eight supported high-level resources, and added direct CLI coverage for `locales list/show`.
- Local onboarding/env writes, token fetch/set, demo writes, and job write rows now produce reviewable `no_snapshot_available` plans and require explicit no-snapshot approval before local file writes, token endpoint calls, row writes, or success receipt output when before-state support is not available.
- Refreshed the tool/public proof surface so the Amazon Creators 100% coverage claim is enforced by tests and reflected in the Qwayk front-door docs.
- Fixed catalog endpoint paths and request payload fields so `SearchItems` and `GetVariations` match the official API reference (and clarified the CLI flags: `--item-count/--item-page`, `--asin`, `--variation-count/--variation-page`).
- Fixed OAuth token fetch to use the correct scope and request format for v2.x (Cognito form) vs v3.x (LwA JSON) credentials.
- normalized the CLI’s global flag parsing so `--apply`, `--env-file` and other global options work anywhere on the command line, matching the docs/examples.
- aligned onboarding/README hints with OAuth token fetch (partner tag + 2.1 version) and cleaned up docs/examples to match the recorded flow.
- scaffolded the Amazon Creators Catalog API CLI with the template base and renamed every entry point to `amazon-creators-api-tool`.
- Added the explicit catalog command surface (`browse-nodes`, `items`, `variations`, `search`), resource presets, locale helpers, safety gates around onboarding/auth token writes, and updated docs/tests/skill assets.
- Prevented credential secrets from leaking in CLI logs/errors and added a regression test that ensures verbose commands never echo the secret.
