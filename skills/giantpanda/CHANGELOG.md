# Changelog

## [Unreleased]

### Added

- Added full public-facing docs pages in `docs/` for first-run, safety, onboarding, and command reference.
- Added wrapper rules under `skills/giantpanda-safe-cli/`.

### Changed

- Rewrote `README.md` with product-specific first screen, approvals, and no-snapshot language.
- Aligned onboarding, command reference, and use-case docs to exact CLI flags and fixed-host behavior.

### Fixed

- Removed placeholder/template-only wording from the GiantPanda front-door docs.
- Refused HTTP redirects instead of following a token-bearing request.
- Bound the reviewed domain-limit and duplicate-removal safety metadata into the approved plan id.
- Fixed onboarding numbering, command reference apply semantics, and auth/read/apply parity docs.
- Added `docs/proof.md` with completed package, linter, installed-wheel, and sanitized provider-live stats proof for this slice.
- Added parser examples and evidence files under `docs/examples/` plus `examples/example.env` with a parse-safe placeholder layout.
- Added focused behavior coverage test for coverage/examples/wrapper/proof alignment and hygiene checks.
