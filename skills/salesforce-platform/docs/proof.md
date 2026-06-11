# Proof

## Last verified

- Date (UTC): `2026-06-04`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider docs version used for implementation: `Salesforce REST API v67.0` and `Bulk API 2.0 v67.0`
- Environment used here: local development only, no live Salesforce org attached

## Verified locally

- `.venv/bin/python -m unittest -q tests.test_salesforce_safety tests.test_run_artifacts`
  - result at verification time: `13 tests, OK`
- `.venv/bin/python -m unittest -q`
  - result at verification time: `30 tests, OK`
- `.venv/bin/python -m unittest -q tests.test_docs_formatting`
  - result at verification time: `1 test, OK`
- `python3 -m json.tool docs/examples/plan.example.json`
- `python3 -m json.tool docs/examples/receipt.example.json`
- parser build and runtime action inventory
  - shipped command count at verification time: `175`
- installed CLI smoke checks
  - `qwayk-salesforce-platform-safe-agent-cli --output json --version`
  - `qwayk-salesforce-platform-safe-agent-cli --output json auth token status`
  - `qwayk-salesforce-platform-safe-agent-cli --output json onboarding --no-write-env`
- write safety reset:
  - write plans include `before_state.required: true`, `before_state.supported: false`, and `verification_plan.type: no-snapshot-approval`
  - write apply requires explicit no-snapshot approval before `HttpClient.request`, so no Salesforce provider write is sent and no write receipt is created

## Not live-verified here

- authenticated reads against a real org
- real writes against live records; current write apply requires explicit no-snapshot approval before provider HTTP until before-state capture support exists
- org-gated areas such as Knowledge, Scheduler, survey translations, Named Query API, consent/Data 360, and the OpenAPI beta
- Bulk API 2.0 live job lifecycle timing and org-specific limits

These areas are documented and implemented, but they are marked as org-gated or live-unverified where appropriate in `docs/api_coverage.md`.

## Live-org smoke commands still not run here

```bash
qwayk-salesforce-platform-safe-agent-cli --output json auth check
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
qwayk-salesforce-platform-safe-agent-cli --output json composite execute --body-file composite.json
```

## Example committed outputs

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (safe refusal example; old filename kept)
