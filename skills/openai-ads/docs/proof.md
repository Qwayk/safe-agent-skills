# OpenAI Ads test results

## November 22, 2026 local checks

The source and local catalog each passed 19 tests from the checkout and a fresh wheel install. Both installs loaded all 40 Advertiser API commands. The source downloads include the skill, setup example, guides, and saved API spec. A fresh install created an editable settings file and reused it in the account-check command.

With simulated Ads replies, a campaign send got one request on a server error. A conversion send got one request on a timeout. Both cases produced a receipt that said the result was unknown. A read still retried after a temporary error. The tests also checked that the event type and tracking window remain visible while private values stay hidden.

I checked the 40 remaining routes against the current official spec. The old audience upload route is gone. Ad groups and ads can now be listed without filtering by their parent. The scope still follows the saved tool inventory. See [API coverage](api_coverage.md).

The CLI type check passed with Python 3.10 analysis settings. The installed mypy version cannot check the repository’s Python 3.9 setting. Ruff reported two existing style issues in `cli.py` and `inventory.py`. These checks used simulated replies and made zero Ads account requests.

## July 6, 2026 record

### What was checked

- The official OpenAI Ads OpenAPI spec was fetched from `https://developers.openai.com/ads/openapi.json` and pinned at `docs/specs/openai-ads-openapi.json`.
- The pinned spec reports OpenAPI `3.1.0`, spec version `2.3.0`, server `https://api.ads.openai.com/v1`, 33 paths, and 41 operations.
- `docs/api_coverage.md` was generated from that pinned inventory and includes manual rows for official measurement docs outside the spec.
- `python3 -m unittest -q` passed with 15 tests.
- `.venv/bin/python -m unittest -q` passed with 15 tests after editable install.
- `.venv/bin/python -m pip install -e .` passed.
- `.venv/bin/openai-ads-safe-agent-cli --output json api list` returned valid JSON.
- `git diff --check` passed for the OpenAI Ads source and touched workspace/control-room docs.

### Behaviors tested

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

### Live behavior in the July 6 build

Live OpenAI Ads behavior is not verified in this source run because no real eligible Ads Manager Beta account, billing, account verification, and Ads API credentials were available. Missing live credentials are not treated as a source-ready blocker; live status is marked honestly.

### Saved July output examples

These saved July examples show the earlier output, including the old command count and preview.

- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
- `docs/examples/outputs/api-list.json`
- `docs/examples/outputs/conversion-plan.json`
