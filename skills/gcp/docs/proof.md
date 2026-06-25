# Proof and verification

Most users will never need to run these commands themselves. This proof page answers what has actually been checked, what was only tested locally, and what still needs a real Google Cloud read before anyone claims live account behavior.

The short version: local tests and generated coverage passed; live Google Cloud account behavior has not been verified yet.

A good evidence request is: "Show me what has already been verified for GCP, what is still live-unverified, and the first safe read needed for real account proof." If you only check one thing, check whether the reported proof came from a local test, a mocked example, a generated coverage ledger, or a real Google Cloud account read.

## What this page proves

- the source tool installs
- the local test suite passes
- the docs contract checks pass
- the generated inventory can be read from the source checkout
- committed examples are redacted safe-shape examples
- mocked examples show expected output shape without pretending a live account was checked

This page does not prove that a real Google Cloud project, server, bucket, IAM policy, database, log stream, or billing account was read successfully.

## Last verified

- Date (UTC): `2026-06-25`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider source: official Google Discovery directory plus official fallback sources for selected gaps
- Environment: local source build; no live Google Cloud account verification yet

## Smoke checks

Run inside the tool folder.

Create the local environment and install:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Check the command:

```bash
qwayk-gcp-safe-agent-cli --output json --version
```

Check local Google credential lookup:

```bash
qwayk-gcp-safe-agent-cli --output json auth check
```

Read the packaged inventory:

```bash
qwayk-gcp-safe-agent-cli --output json inventory summary
```

`auth check` only proves whether Application Default Credentials are available on the machine. `inventory summary` only reads the packaged source inventory. Neither one proves broad live account behavior.

## Latest local validation

Run on 2026-06-25:

- `.venv/bin/python -m pip install -e .` passed.
- `.venv/bin/python -m unittest -q` passed with 54 tests.
- The repo new-tool flow audit passed.
- The control-room project audit passed.
- `git diff --check` passed.

These checks prove local source behavior, docs contracts, and repo alignment. They do not replace a real Google Cloud safe-target run.

## Example outputs

Committed examples live under `docs/examples/`:

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/inventory_summary.json`
- `docs/examples/outputs/auth_check.redacted.json`
- `docs/examples/outputs/compute_instances_list.mocked.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

They are redacted examples or mocked shapes. They are not proof that a live Google Cloud account was changed or read successfully.

## What still needs live verification

Before relying on this with a real account, run a separate safe-target check:

1. Choose a real Google Cloud project and zone that are safe to inspect.
2. Confirm Application Default Credentials and quota context.
3. Run one small read, such as Compute Engine instances, enabled services, a storage bucket list, or Cloud Run services.
4. Confirm whether the result is expected, empty, or blocked by IAM.
5. Only after that, prepare a dry-run plan for one tightly scoped write if a write test is approved.

Do not claim live Google Cloud account verification until that work is actually done.

## What can go wrong

- **ADC is missing.** `auth check` returns a credential error and no write runs.
- **The quota project is wrong.** Google may reject a request even when credentials are valid.
- **IAM is too narrow.** The tool can reach Google Cloud but cannot read the requested resource.
- **The API is not enabled.** A project can have credentials and still reject service-specific reads.
- **An allowlist refuses the target.** The project, folder, organization, billing account, region, zone, or parsed `locations/...` target is outside the local guardrails.
- **Verification is limited.** Generated writes record `read_back_verified: false` unless a real read-back check ran.

## Links

- [API coverage](api_coverage.md)
- [Official references](references.md)
