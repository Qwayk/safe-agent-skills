# Changelog

All notable changes to this tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- Customer-ready proof pack docs under `docs/` (`proof.md`, `references.md`, `api_coverage.md`, `engineering_notes.md`).
- `browse get` command (`GetBrowseNodes`) with deterministic batching and a `--yes` guard.
- `product variations` command (`GetVariations`) with `--variation-page` and `--variation-count`.
- `--resources-preset` and repeatable `--resource` controls for PA-API `Resources`.
- Jobs support for `browse.get` and `product.variations`.
- Agent Skills wrapper docs and `SKILL.md` under `skills/`.

### Changed
- `--version` now emits machine-readable JSON in `--output json` mode (no config/env required); text mode preserves the human-readable version string.
- `product get` now supports deterministic batching for >10 ASINs with `--yes`, `--batch-size`, and `--max-requests`.

### Fixed
- `--output json` now guarantees exactly one JSON object to stdout for parse/usage errors.
