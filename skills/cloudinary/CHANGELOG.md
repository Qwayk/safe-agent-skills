# Changelog

## 2026-06-04

- Added blocked `before_state` and explicit no-recovery metadata to Cloudinary write plans.
- Changed write apply behavior so generated Cloudinary writes require explicit no-snapshot approval before credentials are used for the write or Cloudinary HTTP when command-specific before-state support is not available.
- Kept existing gates first: `--apply`, `--yes`, `--ack-irreversible`, plan drift checks, and `--out` for sensitive write results.
- Updated tests, docs, examples, and skill wrapper for the current plan-only write state.

## 2026-05-25

- Created `cloudinary-safe-agent-cli` from the shared Python API tool starter.
- Added generated allowlist coverage for 175 official Cloudinary REST operations across upload, admin, provisioning, permissions, analyze, live streaming, player profiles, and video config.
- Added dynamic per-operation CLI routing from `docs/_generated/cloudinary_rest_inventory.json`.
- Added Cloudinary `.env` loading for product and account credentials, plus live `auth check` smoke calls.
- Added write safety gates for dry-run, `--apply`, `--yes`, `--ack-irreversible`, and `--out` on sensitive or binary results.
- Added test coverage for all shipped Cloudinary API areas.
- Replaced starter docs and wrapper prompts with Cloudinary-specific docs.
