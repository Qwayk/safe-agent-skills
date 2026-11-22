# HubSpot verification

## November 22, 2026

All 32 tests passed in the source and local catalog copies under Python 3.12. Each built package installed in a fresh environment. Both skills passed the skill validator. All 61 examples in the command guide parsed with the expected approval flags, and local links resolved.

The installed CLI kept the chosen settings file, refused a changed CSV before sending a request, and reported a queued import and a partly successful bulk change correctly. These checks used fake HubSpot replies on this computer and made zero live HubSpot calls.

Run the tests from the tool folder with Python 3.12 or newer:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

The tests cover the shipped commands, setup, saved plans, approvals, multipart uploads, import receipts, and partial bulk failures. They also check local run history and JSON output.

For a quick check after installing the package:

```bash
qwayk-hubspot-safe-agent-cli --output json --version
qwayk-hubspot-safe-agent-cli --env-file 'my settings.env' onboarding --no-write-env
```

For a first account read, use [the quickstart](quickstart.md). For a change, use [the approval steps](safety_model.md).

## June 4, 2026 UTC verification

The maintainers recorded 27 tests passing in the local build of version `0.1.0`, configured for `https://api.hubapi.com`. The record includes version, onboarding, a contact creation preview, and a refusal when approval to proceed without a saved copy was missing.

Commands from that record:

```bash
PYTHONPATH=src python3 -m unittest tests.test_command_families tests.test_hubspot_safety tests.test_hubspot_import_validation tests.test_run_artifacts tests.test_onboarding_command tests.test_auth_redaction tests.test_imports
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m hubspot_safe_agent_cli --output json --version
PYTHONPATH=src python3 -m hubspot_safe_agent_cli --output json --env-file "$tmpdir/.env" onboarding
PYTHONPATH=src python3 -m hubspot_safe_agent_cli --env-file "$tmpdir/.env" hubspot objects create --object-type contacts --body-file "$tmpdir/body.json"
.venv/bin/python -m unittest -q
```

## Saved examples

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [Original preview](examples/plan.example.json)
- [Original approval refusal](examples/receipt.example.json)

The preview and refusal files show the older output for reference. Use a new preview from the current tool before approving a real write.
