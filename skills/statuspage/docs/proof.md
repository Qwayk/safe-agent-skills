# Proof / verification

This page shows how to verify the tool and inspect what it does.
Most users will not need to run these commands themselves.
They are here so you, your reviewer, or your agent can inspect the same path behind the tool.

## Last verified

- Date (UTC): 2026-01-26

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

## Examples (committed)

See `docs/examples/` for:
- fixed sample Status API responses, and
- sample CLI outputs under `docs/examples/outputs/`.
