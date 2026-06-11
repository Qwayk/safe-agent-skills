# Proof pack (publish-ready evidence)

## What is verified in this repository now

### 1) Locally tested now
- Full local suite: `.venv/bin/python -m unittest -q` -> `Ran 22 tests in 2.696s OK`
- CLI version command:
  - `linkedin-ads-api-tool --output json --version`
- Onboarding and token helper commands:
  - `linkedin-ads-api-tool onboarding`
  - `linkedin-ads-api-tool auth token set --file token.json`
  - `linkedin-ads-api-tool auth token status`
- Operation plumbing from `operation_catalog.py`:
  - Family/operation parser wiring
  - Non-read dry-run plan generation (`--plan-out`)
  - Write plans include `before_state.required: true` and `before_state.supported: false`
  - Live write acknowledgement gate (`--ack-irreversible`)
  - High-risk apply gate checks (`--apply`, `--yes`, `--plan-in`)
  - Write apply attempts require explicit no-snapshot approval before LinkedIn HTTP when no saved snapshot is available
- JSON error contract:
  - JSON parse failures return `ok: false` with `error_type`
- Run artifacts:
  - `runs list`
  - `runs show`

Local checks are done in CI through unit tests in this repo.  
All tests write artifacts and run without real network in tests.

## 2) Implemented but live-unverified because access is gated
The CLI command surface is generated from `docs/api_coverage.md` and `operation_catalog.py`, so families exist in runtime and can produce dry-run plans.
Every live write now also requires `--ack-irreversible` and then requires explicit no-snapshot approval before LinkedIn HTTP because this runtime does not provide snapshot restore or provider backup/restore.

Live calls may still fail today if your LinkedIn app is not approved for the required product and permissions.
This is expected for:
- account and creative write endpoints
- campaign and reporting write endpoints
- conversions, lead, targeting and tracking write flows
- most `access-gated` + `tier-gated` operations in covered families

## 3) Documented but private/restricted by LinkedIn
These areas are in scope in the catalog, but LinkedIn marks them private/restricted:
- `account-intelligence`
- `ad-page-sets`
- `ad-segment-sources`
- `ad-segments`
- `audience-insights`
- `dmp-engagement-source-types`
- `dmp-segments`
- `media-planning`
- `media-plans`

For these, a valid token and approved app path are usually required before live calls can succeed.

## Run evidence files in docs/examples

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; kept under the old filename for compatibility)

These files are redacted and aligned to the JSON shapes this tool emits.

## What can still block proof

- `403` from LinkedIn approval gates.
- `401` from expired or wrong token.
- `404` / `410` from private API rollout differences.
- Missing `--output json` when automation expects machine output.
