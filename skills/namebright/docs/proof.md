# Proof and verification

This page only lists checks already completed from source-only review.

## What this proves

- CLI parser and config loading cover the documented command surface.
- Source inspection confirms write commands are plan-first by default and apply requires the reviewed plan.
- No live NameBright endpoint was called in this source build.
- Ruff passed across the source tree.
- mypy passed across 21 source files.
- The complete Python 3.12 suite passed all 103 tests.

## Last verified

- Date (UTC): 2026-07-31
- Verified by: source inspection and file-level checks
- Tool version: 0.1.0
- Provider API version: NameBright Domain + OAuth docs
- Environment: source-only (no live credentials)

## Completed source checks

```bash
python3 -m ruff check .
python3 -m mypy src
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The checks used Python 3.12.13. The tests cover the 61-operation registry and parser, fixed hosts, OAuth request shape and in-memory cache, bounded rate behavior, redaction, all 37 write plans, snapshots and drift refusal, acknowledgements, purchase rechecks, secret-file isolation, verification, receipts, private file modes, coverage alignment, and safe example parsing. Contact-specific tests prove that two different raw contact records produce different snapshot digests and refuse apply before a provider write even when their redacted displays match. They also prove that contact plans and receipts contain only redacted details, non-reversible SHA-256 digests, and safe post-write field names.

## Package checks

Python 3.12.13 built both archives from the final source:

- source archive: `namebright_safe_cli-0.1.0.tar.gz`
- wheel: `namebright_safe_cli-0.1.0-py3-none-any.whl`
- source archive files: 77
- wheel files: 26

The source archive contains the README, changelog, blank environment example, full docs, 61-line checksum manifest, safe examples, tests, and tracked `skills/namebright-safe-cli/SKILL.md`. It contains no `AGENTS.md`, `.env`, `.state`, virtual environment, cache, bytecode, build, or distribution folder. The wheel contains only the Python package and standard distribution metadata.

The unpacked source archive passed the same 103-test suite. A fresh external Python 3.12 environment installed the wheel with its declared dependencies and ran from outside the checkout. The installed CLI returned the expected version JSON and safely refused missing credentials before network access. Direct installed-package checks proved 61 unique commands, 11 families, method totals of 23 GET / 18 POST / 8 PUT / 12 DELETE, both fixed NameBright URLs, no generic/raw/base-URL/token-file/demo/jobs parser surface, a mode-0600 contact-update plan through an injected no-network fake with redacted values and both contact-value and raw-snapshot digests, no source-path import dependency, and no source docs, tests, skills, instructions, state, or environment files inside the installed package.

## Future credentialed smoke checks

These checks were not run during the source build. They require a real credential, an approved source IP, and separate authorization for live NameBright reads. Run them inside the tool folder only when that access is approved:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version check:
- `namebright-safe-cli --output json --version`

3) Connection check:
- `namebright-safe-cli --output json auth check`

4) Representative reads:
- `namebright-safe-cli --output json account show`
- `namebright-safe-cli --output json domains list`

5) Write-safe pattern:
- `namebright-safe-cli --output json --plan-out plan.json domains update --domain example.com --locked true`
- `namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out plan.receipt.json --ack-high-risk domains update --domain example.com --locked true`

## Safe examples

These files are committed, redacted, and provider-free:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

The plan and receipt show the runtime field shape using fake data. Their example fingerprint is intentionally not valid, so they cannot be applied.

## Still live-unverified

No credential, bearer token, live availability check, account read, domain read, or provider write was used. Provider permissions, response details, rate-limit behavior, and read-after-write timing remain live-unverified. Missing live proof does not weaken the local plan and refusal tests, but it must not be described as live NameBright proof.
