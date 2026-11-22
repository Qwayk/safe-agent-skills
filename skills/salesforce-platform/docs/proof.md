# Salesforce verification

## November 22, 2026

Both local copies passed all 34 tests and installed from a built package outside the checkout. Both skill files passed validation, and 29 documented command examples parsed.

The installed tool kept the selected settings file, read a test account, and refused changed request options before sending a write. It distinguished a submitted bulk job from completion and reported a grouped request with a failed item. The tests also checked the extra approval for starting a permanent bulk delete. These checks made no live Salesforce calls.

Run the checkout tests with Python 3.12 or newer:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Use fake Salesforce replies for package checks away from the source folder.

## June 4, 2026 UTC verification

- Date (UTC): `2026-06-04`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider docs version used for implementation: `Salesforce REST API v67.0` and `Bulk API 2.0 v67.0`
- Environment used here: local development only, no live Salesforce org attached

### Checks recorded at the time

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
  - the check confirmed that the command stopped before `HttpClient.request` when approval to proceed without a saved copy was missing

## Live checks still open

- authenticated reads against a real org
- writes and read-back in a real Salesforce org
- org-gated areas such as Knowledge, Scheduler, survey translations, Named Query API, consent/Data 360, and the OpenAPI beta
- Bulk API 2.0 live job lifecycle timing and org-specific limits

See [API coverage](api_coverage.md) for org features and permissions these commands may need.

## Example commands for a real org

```bash
qwayk-salesforce-platform-safe-agent-cli --output json auth check
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
qwayk-salesforce-platform-safe-agent-cli --output json composite execute --body-file composite.json
```

## Saved output

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [Original preview](examples/plan.example.json)
- [Original refusal](examples/receipt.example.json)

The original preview and refusal show the older output. Save a new plan with the current tool before approving a real change.
