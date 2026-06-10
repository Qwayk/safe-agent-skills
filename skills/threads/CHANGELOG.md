# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Wave 4 before-state reset for write safety:
  - Write dry-run plans now include blocked `before_state`.
  - Confirmed apply attempts refuse before Threads provider writes, local token writes, demo/job writes, or receipt output.
  - Example plan/receipt files now show the current no-snapshot approval shape.
- Official Threads command surface for auth, profiles, posts, replies, mentions, insights, keyword search, locations, and oEmbed.
- Threads-safe skill wrapper and endpoint coverage ledger.
- Local unit coverage for request paths, parser shape, and write-plan safety.

### Changed
- Post creation now sends official Threads payload shapes, including `media_type`, poll objects, GIF objects, text spoiler entities, reply approvals, and carousel rules.
- Docs, proof, examples, and wrapper guidance now match the shipped CLI surface.

### Fixed
- `posts create-*` commands now map to the documented Threads publishing surface instead of partial scaffold payloads.
- `posts list-public`, token refresh, keyword search, location search, reply moderation, and oEmbed request shapes follow the official Threads docs.

### Removed
- Undocumented public CLI commands for ghost posts and user-replies listing.
