# Proof and verification

Statuspage proof should answer a simple question: what has actually been checked for public incidents, components, maintenances, subscribers, and status summaries, and what can still fail because of public API limits, changed upstream data, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check incident, component, maintenance, and status examples before trusting a status report.

## Current proof summary

These checks show how to verify the skill and inspect what it does.
Most users will not need to run these commands themselves, but the same path is here for a reviewer or agent to inspect.

## Last verified

- Date (UTC): 2026-06-11

## Intended environment

- Environment: public status site / base URL: `https://status.atlassian.com`

## Local verification

```bash
python3 -m pip install -e .
python3 -m unittest -q
```

## Optional live smoke (calls public endpoint)

```bash
statuspage-api-tool --output json --base-url https://status.atlassian.com status get
```

The live smoke is read-only and checks the real public page path.

## Examples (committed)

See `docs/examples/` for:
- fixed sample Status API responses, and
- sample CLI outputs under `docs/examples/outputs/`.
## What can go wrong

- The public page can change between runs, so compare timestamps before treating a status summary as final.
- A network or provider error can block the live smoke even though the tool remains read-only.
- Fixed examples prove output shape, not the current live state of a status page.
