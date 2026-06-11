# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Changed
- Dynadot write plans now disclose `no_snapshot_available` when no useful before-state can be saved; reviewed write apply requires command-specific before-state support or explicit no-snapshot approval before Dynadot HTTP.
- API3 writes, domain push, push-request accept/decline, name-server set, transfer run, demo writes, and jobs writes no longer produce write receipts while before-state is unsupported.
- `domains name-servers set` now treats the Dynadot `server_list` availability check as clearly advisory by default, which makes external providers like Cloudflare less confusing.
- `runs list` and `runs show` now filter to Dynadot tool rows only, even when the local run index contains mixed tools.
- API3 write plans may retain read-back details as `post_apply_verification_plan`, but those notes do not unlock apply while before-state is unsupported.

### Fixed
- `dynadot-api-tool --help` no longer crashes on the API3 help text.
- `domains name-servers set` now correctly prefers the real `changes` list from diff files even when `to_change` is only a count integer.
- Cleaned up internal template leftovers and clarified the write safety contract.
- Removed an accidentally-committed local artifact file that is supposed to be gitignored.

## [0.5.0] - 2026-02-25

### Added
- `api3/` command group providing first-class CLI subcommands for every official Dynadot API3 `command=` value (100% coverage).
- Standardized write gating for `api3` writes: dry-run plan by default; apply requires `--apply --yes --plan-in`; irreversible/monetary actions also require `--ack-irreversible`.

### Changed
- `docs/api_coverage.md` now records 100% coverage via `api3/` subcommands.

### Fixed
- Removed deprecated `backorder-auctions open` command from the official command set snapshot (and from this CLI) because the current Dynadot docs no longer include a request example URL for it.

## [0.4.13] - 2026-02-25

### Added
- New read-only commands:
  - `closeouts list`
  - `backorders requests list`
  - `cn-audit status`

## [0.4.12] - 2026-02-24

### Added
- New read-only commands:
  - `transfers list`, `transfers status`, `transfers auth-code`
  - `orders list`, `orders status`
  - `contacts list`, `contacts get`
  - `dns get`
  - `marketplace listings list`, `marketplace listings get`
  - `auctions open`, `auctions closed`, `auctions details`, `auctions bids`
  - `backorder-auctions open`, `backorder-auctions closed`, `backorder-auctions details`

### Changed
- Read-only auctions/marketplace commands now match Dynadot docs: currency support, corrected required params, and removed unsupported flags.

## [0.4.11] - 2026-02-15

### Added
- `transfer run`: `--verification-mode fast` to reduce verification API calls on large batches (presence spot-check + skip name server verification).

### Fixed
- Transfer run: speed up receiver accept step when Dynadot returns “No push order found …” by refreshing the push-request queue and retrying only domains that are still pending (avoids slow per-domain retries).
- Transfer run: treat “No push order found …” errors during the accept retry as warnings and re-check the push-request queue before falling back to per-domain accepts.

## [0.4.10] - 2026-02-15

### Fixed
- Transfer run: treat receiver-side “No push order found …” accept errors as warnings (when domains are confirmed present), so successful runs don’t report false failures.
- Transfer run receipts now set `changed=true` when any push/accept/name-server changes were applied, even if the run was partial.

## [0.4.9] - 2026-02-15

### Fixed
- Transfer run resume now skips `failed_domains` as well (so known blocked domains don’t get re-selected every batch).

## [0.4.8] - 2026-02-15

### Fixed
- Dynadot API client retries once automatically on “Too many requests… try again in 1 minute” rate limits (helps large runs complete).
- Transfer run resume now skips both `done_domains` and `failed_domains` from the resume receipt, and selection fills the requested batch size without getting “shrunk” by skipped domains.

## [0.4.7] - 2026-02-13

### Fixed
- Transfer run push/accept now falls back to per-domain retries when a batch write fails without naming a specific domain, so one problematic domain (example: `.us` receiver nexus setup) doesn’t block progress for the rest.

## [0.4.6] - 2026-02-13

### Fixed
- Transfer run now paces receiver `get_ns` reads using `--ns-sleep-between-verifications-s` to reduce rate-limit errors on large batches.

## [0.4.5] - 2026-02-13

### Fixed
- Transfer run reruns no longer fail just because domains already left the sender account; sender eligibility checks only run for domains that still need pushing.
- Transfer run receipts now mark `partial=true` whenever any domains failed.

## [0.4.4] - 2026-02-13

### Fixed
- Transfer run excludes domains whose expiration date is in the past (even if Dynadot still reports `Status=active` during grace).
- Transfer run push/accept steps record per-domain failures when Dynadot error messages name specific domains.

## [0.4.3] - 2026-02-13

### Fixed
- Transfer run presence checks now use receiver `domain_info` (reliable even when the receiver account has many domains / pagination).

## [0.4.2] - 2026-02-13

### Fixed
- Transfer run apply now reports push/accept failures as `failed_domains` (instead of leaving them as `remaining`).
- Transfer run apply avoids extra presence / name-server checks when nothing is expected to be in the receiver yet.
- Clearer hint when Dynadot blocks pushes due to sender account lock (“Please unlock your account firstly.”).

## [0.4.1] - 2026-02-12

### Fixed
- Multi-account safety: the receiver `--receiver-env-file` now ignores OS env var overrides.
- Transfer apply safety: re-checks sender domain status at apply time and enforces `active` only by default.

## [0.4.0] - 2026-02-12

### Added
- Guided end-to-end transfer workflow:
  - `transfer run` (push sender → accept receiver → confirm → check/fix name servers → summary)
  - Active-only selection (`domain_info.Status == active`)
  - Safe resume via `--resume-from-receipt` (skips already done domains)

### Fixed
- CLI `--version` output now matches the packaged version.

## [0.3.1] - 2026-02-11

### Added
- Safe resume support for large runs:
  - `--resume-from-receipt` for `domains push`
  - `--resume-from-receipt` for `domains push-requests accept/decline`
  - `--resume-from-receipt` for `domains name-servers set`
- Verification pacing for name server bulk sets:
  - `--sleep-between-verifications-s` for `domains name-servers set`
- Optional name server availability pre-check (Dynadot account):
  - Warn by default; can refuse apply with `--require-available-name-servers`

## [0.3.0] - 2026-02-11

### Added
- Name server audit + bulk set commands (safe-by-default):
  - `domains name-servers export` (read-only export of current name servers per domain)
  - `domains name-servers diff` (compute changes vs desired name servers)
  - `domains name-servers set` (preview-first; apply-gated with `--apply --yes --plan-in`; read-back verification via `get_ns`)

## [0.2.0] - 2026-02-10

### Added
- Read-only inventory exports:
  - `domains list` (paged + `--all`, with optional `--out` JSON export)
  - `domains info` (per-domain `domain_info`, with optional `--out`)
  - `domains status` (derived from `domain_info`, with optional `--out`)
  - `domains folders list` (folder groups via `folder_list`, with optional `--out`)
- Bulk write pacing/limits:
  - `--sleep-between-batches-s`
  - `--max-batches` (supports intentional partial completion; receipts include `partial: true`)

### Changed
- CLI command wiring is registered via a central command registry for easier safe extension.

## [0.1.3] - 2026-02-10

### Added
- Clear “Push Username” wording and a safer CLI flag (`--to-push-username`, with `--to-username` kept as an alias).
- References now include the official Dynadot “Push Username” help page.

### Changed
- Proof page wording is now explicit that verification here is local tests only (no live account run).

## [0.1.2] - 2026-02-10

### Security
- High-risk apply steps require a reviewed plan file (`--plan-in`) for:
  - domain push,
  - push-request accept/decline,
  - jobs that include write actions.

## [0.1.1] - 2026-02-10

### Fixed
- Push-requests parsing now matches the Dynadot API response shape (`pushDomainName`).

## [0.1.0] - 2026-02-10

### Added
- Phase 0 foundation: docs, progress tracking, safety model, proof pack, and skill wrapper.
- Phase 1 domain push workflows:
  - Sender: push domains to another Dynadot account (bulk, chunked, auto-unlock for push by default).
  - Receiver: list incoming push requests; accept/decline in bulk with verification.

### Fixed
- JSON output contract for CLI usage errors (argparse handled safely).
