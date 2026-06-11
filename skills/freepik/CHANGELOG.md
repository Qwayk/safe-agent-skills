# Changelog

## Unreleased

- Rebuild the public-facing README and linked docs so they match the real approved `--ack-no-snapshot` download flow, update example JSONs, and add contract tests for the Freepik public page and approved apply behavior.
- Licensed download apply now requires real before-state support or explicit no-snapshot approval before the Freepik download/license endpoint, binary fetch, destination file write, or inventory row write. Dry-run plans include `no_snapshot_available` before_state metadata.
- Precheck hygiene for standalone export: empty `FREEPIK_API_KEY` in `.env.example`, add `examples/example.env`, harden `.gitignore`, and remove monorepo-specific install paths from docs.
- Add customer-ready proof pack docs under `docs/` (proof, references, API coverage, examples).
- Add Agent Skills wrapper docs and a Codex skill package under `skills/`.
- Add `search photos` with photo-first defaults plus `--shortlist` and `--write-jobs` helpers.
- Add `resource shoot-pack` plus grouped related extraction in `resource related`.
- In `--output json` mode, emit exactly one JSON object on parse/usage errors.
- Refuse overwriting an existing destination file on download unless `--force` is provided.
