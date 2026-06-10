# API coverage (endpoints → CLI)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Give the reviewer one clear reference for review and approval.
- Help customers quickly see what the tool can and cannot do.

Rules:
- Keep this table honest. If something is missing, list it as missing.
- If behavior differs from the provider docs, note it and link `docs/references.md`.

## Summary

- Provider: Google Tag Manager API v2
- API base URL: `https://tagmanager.googleapis.com/`
- Auth methods: OAuth (refresh token), service account JSON, ADC
- Coverage reference: vendored discovery snapshot at `src/gtm_api_tool/_vendor/tagmanager_v2_discovery.json`
- Canonical inventory files:
  - `docs/official_methods_v2.txt` (one discovery `method.id` per line)
  - `docs/official_commands_v2.txt` (one CLI command per line, derived from method ids)
- Last audited (UTC): 2026-03-02

## What “100% coverage” means (for this tool)

100% coverage means: every discovery method id in the vendored snapshot has a first-class CLI subcommand, and the tool exposes that method with deterministic arguments and safety gates.

## Method inventory

This API is tracked by discovery method id rather than a hand-written endpoint table.

- Canonical methods list: `docs/official_methods_v2.txt`
- Canonical CLI surface: `docs/official_commands_v2.txt`
