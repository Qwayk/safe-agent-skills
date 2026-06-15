# Proof and verification

Plausible proof should answer a simple question: what has actually been checked for sites, stats, goals, shared links, team members, and account settings, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check stats/site proof and goal or shared-link plan evidence before trusting analytics changes.

## Current proof summary

Last verified (UTC): 2026-06-01

## Smoke commands (safe)

All commands below are safe to run locally; they do not print secrets.

- Install (minimal): `python3 -m venv .venv && . .venv/bin/activate && .venv/bin/python -m pip install -e .`
- Optional (dev extras): `.venv/bin/python -m pip install -e '.[dev]'`
- Version (JSON): `python3 -m plausible_api_tool --output json --version`
- Config/auth sanity (requires valid env file): `python3 -m plausible_api_tool --output json --env-file .env auth check`
- Stats query from file (read-only): `python3 -m plausible_api_tool --output json --env-file .env stats validate --file examples/goals_list_query.json`
- Sites list (read-only; requires valid env file): `python3 -m plausible_api_tool --output json --env-file .env site list`
- Events dry-run plan (no write; requires valid env file): `python3 -m plausible_api_tool --output json --env-file .env event send --name test_event --url https://example.com/ --referrer https://example.com/from --revenue-currency USD --revenue-amount 9.99`

## What can go wrong

- **Auth blocked** (Stats API): missing/invalid `PLAUSIBLE_API_KEY` or wrong `PLAUSIBLE_BASE_URL`.
- **Query rejected**: invalid Stats API v2 query JSON shape (use `stats validate`).
- **Event approval or refusal**: event send needs explicit no-snapshot approval when before-state persistence is unavailable; domain/host mismatch or props that look like PII still refuse.
- **Sites write refused**: missing `--apply`/`--yes`, or missing `--ack-irreversible` for destructive operations.
- **Sites permission errors**: some destructive endpoints require an owner API key for the site.
- **Recovery mismatch**: verify write plans and receipts expose `recovery`, and confirm the end state is either `irreversible_and_clearly_labeled` or `rollback_by_inverse_action`.
- **Guest-delete rollback drift**: `site guests delete` is reversible only when the command captures the guest's previous role; otherwise it stays irreversible.
- **Before-state gaps**: `event send` and `site shared-links ensure` do not persist `before_state`, so plan/receipt must treat these as intentionally non-reversible by design.

## Proof artifacts (committed, redacted)

- Example outputs: `docs/examples/outputs/`
- Sites example output (synthetic): `docs/examples/outputs/site_list_ok.synthetic.json`
- Event dry-run output example (irreversible): `docs/examples/outputs/event_send_dry_run.json`
- Example plan (inverse-action family): `docs/examples/plan.example.json`
- Example receipt (inverse-action family): `docs/examples/receipt.example.json`
