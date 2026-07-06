# Proof

Last updated: **2026-07-06**

## What was checked

- The official OpenAI Ads OpenAPI spec was fetched from `https://developers.openai.com/ads/openapi.json` and pinned at `docs/specs/openai-ads-openapi.json`.
- The pinned spec reports OpenAPI `3.1.0`, spec version `2.3.0`, server `https://api.ads.openai.com/v1`, 33 paths, and 41 operations.
- `docs/api_coverage.md` was generated from that pinned inventory and includes manual rows for official measurement docs outside the spec.
- `python3 -m unittest -q` passed with 15 tests.
- `.venv/bin/python -m unittest -q` passed with 15 tests after editable install.
- `.venv/bin/python -m pip install -e .` passed.
- `.venv/bin/openai-ads-safe-agent-cli --output json api list` returned valid JSON.
- `git diff --check` passed for the OpenAI Ads source and touched workspace/control-room docs.

## Command proof

Behavior tests cover:

- imports
- `--version`
- `api list`
- generated write dry-run plans
- refusal when apply has no reviewed plan
- private audience/customer/measurement body redaction across stdout, saved plans, audit logs, run summaries, and run indexes
- provider error redaction for private audience/customer/measurement values
- apply receipt redaction for private provider response values
- body-aware high-risk detection for budget, active status, and targeting fields
- refusal when a body-driven high-risk write lacks `--ack-irreversible`
- conversion-event dry-run redaction
- run artifacts for write plans
- audit-log redaction

## Live behavior

Live OpenAI Ads behavior is not verified in this source run because no real eligible Ads Manager Beta account, billing, account verification, and Ads API credentials were available. Missing live credentials are not treated as a source-ready blocker; live status is marked honestly.

## Example outputs

Saved redacted examples live under `docs/examples/`.

- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
- `docs/examples/outputs/api-list.json`
- `docs/examples/outputs/conversion-plan.json`
