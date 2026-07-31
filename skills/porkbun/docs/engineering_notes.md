# Engineering notes

## 2026-07-31

- Replaced template README/docs/examples with Porkbun-specific material.
- Kept command surface aligned to `docs/command_reference.md` and `docs/api_coverage.md` (53 paths / 66 operations).
- Added `skills/porkbun/SKILL.md` for tracked wrapper behavior.
- Replaced placeholder job/token/auth flow docs with Porkbun key-based flow and no batch/job mode.

## 2026-07-31

- Documented corrected safety rules from the latest runtime review:
  - all three billable operations require `--ack-spend`
  - `domainCreate` requires `--ack-terms` and `agreeToTerms` in input
  - no confirmation state defaults now route through snapshot checks and `--ack-no-snapshot` when required

## 2026-07-31 — governor safety and privacy correction

- Replaced recomputable plan integrity with a local owner-only HMAC signing key and signature-first apply validation.
- Rebuilt static apply acknowledgements from current operation metadata and made billable cost checks fail closed.
- Added shared private atomic file handling for keys, plans, receipts, onboarding env files, and secret results.
- Reserved secret output files before provider calls and cleaned empty reservations on failure.
- Disabled redirect following and rejected `3xx` responses.
- Added value-aware secret scrubbing to normal output and every structured error path.
- Changed account invite-status token input from literal `--token` to file-only JSON `--input`.
- Kept the official 53-path, 66-command boundary unchanged and performed no live Porkbun request.

## 2026-07-31 — final local-file and concurrency correction

- Added role-aware collision checks for active plan, receipt, and secret outputs against one another and against environment, JSON input, and plan input files.
- Covered default paths, relative/absolute and `..` aliases, symbolic links, and existing files with the same identity before provider calls or replacement.
- Changed first-use plan-signing-key initialization to create-if-absent so concurrent plan creators share one key.
- Kept private `0700` directories and `0600` files during concurrent initialization.
