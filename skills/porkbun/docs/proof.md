# Proof and verification

Proof is split into two parts: what is proven from code and what is intentionally not live-checked.

- Provider boundary: official v3.9, pinned SHA-256 `f4788709c27e0365e8a502180e0427bbcf7bd7558f3d7032bf34cf0a25dedd77`
- Coverage: `docs/api_coverage.md`
- Command surface: `docs/command_reference.md`
- Wrapper: `skills/porkbun/SKILL.md`

## What this tool can prove in this repository

- deterministic command inventory and coverage file generation
- command parsing and argument shape
- safety path for explicit write commands
- authenticated plan integrity, metadata-based acknowledgement gates, and strict billable cost drift checks
- private atomic local files, role-aware path-collision refusal, concurrency-safe signing-key initialization, and provider-call preflight for secret destinations
- redirect refusal and output/error secret scrubbing
- package and type checks for source
- no placeholder template names in public/docs flow

## What it does not prove

- No live Porkbun account behavior is authorized in this build track.
- No real registration, DNS change, payment, or password update was performed.
- No credential or secret was ever used.
- Mocked transports prove local behavior only. They do not prove Porkbun account permissions, provider response details, or live write/readback behavior.

## Last verified

- Date (UTC): `2026-07-31`
- Scope: source tool package
- Tool version: `0.1.0`
- Provider API version: `3.9`
- Verified base URL(s): `https://api.porkbun.com/api/json/v3`, `https://api-ipv4.porkbun.com/api/json/v3`

## Suggested checks

Run inside the source folder with a clean `.venv`:

1. `python3 -m venv .venv`
2. `.venv/bin/python -m pip install -e '.[dev]'`
3. `.venv/bin/python -m unittest -q`
4. `.venv/bin/ruff check .`
5. `.venv/bin/mypy src`
6. `.venv/bin/python scripts/generate_inventory.py` (or compare with committed files)

The safety tests include recomputed-hash plan forgery, dynamic snapshot and expiry/idempotency tampering, invalid signing keys and signatures, absent or changed billable cost, unsafe secret destinations with zero provider calls, output/control path aliases with zero provider calls or replacement, concurrent first-use signing-key creation, private modes under a permissive umask, atomic replacement, redirect refusal, and secret sentinels across JSON and text error paths.

## Example proof artifacts

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

These are redacted examples to show output shape only.
