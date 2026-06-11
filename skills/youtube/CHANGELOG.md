# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- YouTube Data API v3 pinned discovery snapshot (`docs/official_discovery_youtube_v3_rest.json`) and method inventory (`docs/official_methods.txt`).
- `youtube-api-tool methods list` for local discovery inventory inspection.
- Explicit per-method CLI commands for every pinned discovery method: `youtube-api-tool api <resource.method>` (plan-first; offline-testable).
- OAuth login helper: `youtube-api-tool auth login --console` (plans/refuses before token writes; never prints token values).
- Media upload planning support for discovery `mediaUpload` methods (minimum: `videos.insert`) with dry-run plans that never embed file bytes and confirmed apply refusal before upload endpoint use.
- Media download support for `supportsMediaDownload` GET methods via `--download-to <path>` (example: `captions.download`), including file `sha256` and size in JSON output.
- Blocked write-apply verification plans that confirm no provider write/upload/token write/success receipt happened before before-state support exists.
- First-class channel workflows:
  - `youtube-api-tool channels resolve` (resolve channelId from URL/handle/username/query; safe refusal when selection is required).
  - `youtube-api-tool channels export` (export an analysis-ready dataset of all public channel videos using only YouTube Data API v3).
- Public README contract checks for the source skill page and quickstart opening.

### Changed
- Non-GET API calls, media uploads, auth login/token set, demo writes, and write jobs now produce reviewable plans and require explicit no-snapshot approval before provider/local writes when before-state/provider-backup support is not available.
- Renamed tool identity to `youtube-api-tool` / `youtube_api_tool` and updated docs/tests accordingly.
- HTTP logging and errors redact secret-bearing URLs/headers (query params like `key=` and Authorization).
- Removed the generic dispatcher `youtube-api-tool api call --method ...` and replaced it with explicit per-method commands: `youtube-api-tool api <resource.method> ...`.
- Rebuilt the public README opening and user-facing docs for clearer setup, safety, proof, and YouTube-first task framing.

### Fixed
- Ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- Removed the public proof-page link to source-only helper notes.

### Removed
