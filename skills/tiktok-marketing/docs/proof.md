# Proof pack (publish-ready evidence)

## Last reviewed

- Date (UTC): `2026-06-04`
- Tool version: `0.1.0`
- Provider API version: pinned manifest `official_operations_v1_2026-05-24.json`
- Environment: `https://business-api.tiktok.com` base URL

## Local tested (no external network)

These checks were verified locally in this repo:

You don't need to run these commands yourself... they exist for auditing and proof.

- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e '.[dev]'`
- `.venv/bin/python -m unittest -q`
- `.venv/bin/tiktok-marketing-api-tool --output json --version`
- `.venv/bin/tiktok-marketing-api-tool --env-file examples/example.env --output json api ops list --method GET`
- `python3 -m unittest -q` with `PYTHONPATH=src`
- `--output json --version`
- `api ops list` returning 240 operations from the pinned manifest
- `api ops show --op <operation_command>`
- read-plan generation for `campaign-get`
- multipart plan/refusal flow for `bc-image-upload` with no provider HTTP on apply
- `auth check` with token file fallback and mocked HTTP response

## Live-unverified / access-gated

These require valid TikTok credentials and access to live endpoints:

- `auth check` against the live auth endpoint.
- Any read `api` call with `--live`.
- Future write operations with real before-state support.

For a fresh environment, these are expected to return auth/network errors until config is complete.

## Committed example outputs

These are redacted representative examples from the current runtime. For live-only paths, the examples were produced with mocked provider responses instead of a live TikTok account.

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; approved apply emits a receipt that records no-snapshot approval)

## What can go wrong

- **Invalid app/token settings** → run `onboarding` and `auth check`; verify required env values.
- **Missing required inputs** → check error type `ValidationError` or refusal reasons and re-run with full params.
- **Write safety drift** → write applies should refuse with `before_state.status="blocked"` when no saved snapshot is available.
- **Provider success shape mismatch** → this tool treats non-zero TikTok `code` values as failures even on HTTP 200 responses.
