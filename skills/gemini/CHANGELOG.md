# Changelog

## [Unreleased]

### Changed

- Setup creates a private settings file at the chosen path and shows the next two commands.
- Requests that can cost money need spending approval. Starting a batch job also needs a reviewed plan.
- Saved plans check the key, request and upload before sending. A second apply of the same plan stops before contacting Gemini.
- Run logs leave out the request text. Receipts show when Gemini did not reply and the result needs checking.
- Shorter setup, approval and command guides explain the new steps.

### Added

- Initial Gemini API safe CLI source build.
- Pinned official `v1beta` and `v1` Generative Language discovery documents.
- Generated 82-operation explicit command registry.
- Plan-first safety gates for Gemini state-changing operations.
- Gemini-specific README, docs, coverage ledger, proof notes, and skill wrapper.
- Verified `multipart/related` request bodies for metadata-plus-media uploads.
