# Proof and verification

This source build is verified without Xero credentials and without any live Xero request. It proves the pinned boundary, local behavior, safety failures, package contents, and installed CLI behavior. It does not prove live account permissions or provider outcomes.

## Verified boundary

- Xero OpenAPI release: `16.1.0`
- Pinned commit: `e952d0bda3628facbf7afc5990ad6a0e7e77bd1e`
- OpenAPI operations accounted for: `477`
- Official manual eInvoicing operations: `2`
- Fixed commands: `474`
- Superseded compatibility rows without duplicate commands: `5`
- Callback-only webhook specs: `1`

## Reproducible local checks

```bash
.venv/bin/python -m unittest -q
XERO_OPENAPI_CHECKOUT=/path/to/pinned/Xero-OpenAPI .venv/bin/python -m unittest -q
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src
.venv/bin/python scripts/generate_xero_inventory.py \
  --spec-root /path/to/pinned/Xero-OpenAPI
.venv/bin/python -m build --outdir /tmp/package-output
```

The 2026-07-19 source verification produced these results:

- default `python -m unittest -q`: 88 tests passed, with the one pinned-checkout test skipped when `XERO_OPENAPI_CHECKOUT` was intentionally unset
- fresh pinned-checkout `python -m unittest -q`: all 88 tests passed against `/tmp/qwayk-xero-openapi-round2.RTCw9T/repo`
- `ruff check src tests scripts`: passed
- `mypy src`: passed across 24 source files
- deterministic regeneration: both generated files matched byte for byte
- catalog SHA-256: `d62c9c6acf60ec5c556c4cf66fd779fe1704cc7ef87d34a4dd51af95ae8fc004`
- coverage SHA-256: `69b1ce7fd5a31279b4fb504d4f88d0a4314493ae591e8fedcea55d6ec189bf90`
- source distribution: 1,900,083 bytes, SHA-256 `57a9f384dbf2f427dd24781d5527e08e6f9eeb20a01cc0f16a86b0d645d5d451`
- wheel: 2,030,012 bytes, SHA-256 `67482a68e4b147dce04b25751067b5f3c486f09a4cd6f86a8415ee74eefb8372`
- package content inspection: the generated catalog and registry were present, the retired scaffold command package was absent from both archives, all four packaged App Store rows carried the same XASS lifecycle warning without a guessed endpoint shutdown date, and every affected file included in each archive ended with exactly one newline
- clean wheel install: passed with Python 3.12 in `/tmp/qwayk-xero-installed-round3.3DjYYR`
- installed boundary check: passed for catalog counts, fixed command surface, one-object JSON, protected read output, plan-first writes, changed-file refusal, absence of the retired scaffold command package, and the App Store legacy lifecycle warning
- installed onboarding check: passed and created the placeholder env file with mode `0600`
- exact new-file staging check: all six corrected files were copied byte for byte into `/tmp/qwayk-xero-new-file-check-round3.B5NtYT`, staged as new files, and passed `git diff --cached --check` with no output
- wrapper skill validation, Markdown link validation across 25 files, ignored-secret-path checks, and `git diff --check`: passed

The installed check used fake provider responses only. It did not make a live Xero request.

## Behavior covered by tests

- exact pinned source, family counts, methods, hashes, and deterministic generation
- all callable catalog rows exposed as fixed commands, with no generic request bridge
- current/superseded, regional, access-gated, non-tenanted, callback-only, unavailable, and legacy XASS lifecycle classifications
- minimum-scope PKCE, profile-bound client credentials, private token rotation, exact organisation tenant selection, and Custom Connection target separation
- recursive request validation, missing scope, wrong region, unknown input, protected-header, changed target, and tampered-plan refusals
- all-leaf sensitive read redaction and protected raw output
- write planning, one-use plan execution, uploaded-file change refusal, high-risk approval, no-snapshot approval, idempotency, partial provider responses, DELETE absence verification, and receipts
- exactly one JSON object for CLI success and failure

## Live facts still unverified

No live Xero credential, organisation, payroll account, partner entitlement, paid Custom Connection, App Store entitlement, or gated API was used. Xero may still reject a real request because of account permissions, role, product plan, certification, commercial terms, provider-side validation, rate limits, or changed live behavior.

See [the complete coverage ledger](api_coverage.md), [official sources](references.md), and [example plan and receipt](examples/).
