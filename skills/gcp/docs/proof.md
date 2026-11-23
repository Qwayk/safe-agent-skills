# Google Cloud test results

## November 23, 2026 local checks

The source and local catalog copies each passed 40 tests after a fresh install. I ran the installed command outside the repo. It loaded all 175 services and 9,781 operations from the packaged inventory. The inventory matches the June 25 file byte for byte. Onboarding kept the selected settings filename, created it with private permissions and left it intact on a second run.

With simulated Google replies, the tests checked that changing the identity, quota project, endpoint, input or approval requirements stops a write. They checked the spending approval for a VM start and a billing link, and confirmed that a queued operation, a failed operation and a lost reply leave receipts. I also checked the skill files. These checks ran without calling Google. This update is local.

## June 25, 2026 source checks

Codex checked version `0.1.0` on June 25, 2026 UTC. The inventory came from Google Discovery and selected official fallback sources. The original source check recorded these results:

- `.venv/bin/python -m pip install -e .` passed.
- `.venv/bin/python -m unittest -q` passed with 54 tests.
- The repo new-tool flow audit and the control-room project audit passed.
- `git diff --check` passed.

## Repeat a local check

From the tool folder, install and check the CLI with Python 3.12 or later:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-gcp-safe-agent-cli --output json --version
.venv/bin/qwayk-gcp-safe-agent-cli --output json inventory summary
.venv/bin/python -m unittest -q
```

## What still needs a real account

Run `qwayk-gcp-safe-agent-cli --output json auth check` with the intended Google account. Then [read one resource you know](quickstart.md) and confirm the result with that project, quota project and IAM access. A change needs its own [plan and approval](safety_model.md). A successful Google reply is limited verification until you read the affected resource.

## Saved examples

The [examples](examples/) contain redacted or simulated outputs for the version, command inventory, credential check and Compute Engine read. The saved plan and receipt examples show the original June 2026 fields. Generate a new plan with `--bind-adc` for the current workflow. [API coverage](api_coverage.md) · [Official sources](references.md)
