# Proof and verification

Instagram proof should answer a simple question: what has actually been checked for media, comments, mentions, messages, insights, and token-related work, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check media/account reads, token handling, and write-plan evidence before trusting Instagram work.

## Last verified

- Date (UTC): `2026-06-04`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider API version: default `v25.0`
- Environment: local unit-test workspace / base URL `https://graph.instagram.com`

Live Meta auth was not run in this workspace because no Instagram professional-account credentials were provided here. The proof pack below covers the shipped CLI shape, local auth safety, redaction, before-state plans that require explicit no-snapshot approval, missing-approval refusals, and unit-test validation.

## Smoke checks

Run inside the tool folder:

1. Create venv and install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2. Version output without `.env`:
- `instagram-api-tool --output json --version`

3. Local auth status without printing tokens:
- `instagram-api-tool --output json auth token status`

4. Safe blocked auth example when no token is present:
- `instagram-api-tool --output json --env-file .missing-env auth check`

5. Full local validation:
- `.venv/bin/python -m unittest -q`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; approved apply emits a receipt that records no-snapshot approval)

## What can go wrong

- **Missing or expired token** → verify with `auth token status` or `auth check` returning `ok=false` and a clear error type; confirm no remote write occurred.
- **Rate limiting** → verify the CLI surfaces a redacted HTTP failure and never leaks tokens in the URL or response text.
- **Wrong OAuth exchange shape** → verify `auth code exchange` uses `POST /oauth/access_token` and treats OAuth error payloads as failures.
- **Secret leakage in logs or errors** → verify auth-path failures redact `client_secret`, `code`, and token-like values.
- **Write safety drift** → verify write plans include `before_state.status="blocked"` and confirmed apply attempts require explicit no-snapshot approval before Instagram HTTP, local token-file writes, or receipt output.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
