# Command reference

Use this page when you need the exact Statuspage command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Setup

You need a target public status page.
Use one of these:

- pass `--base-url https://status.somevendor.com`
- or keep `STATUSPAGE_BASE_URL=https://status.somevendor.com` in a local `.env`

## Version / help

- `statuspage-api-tool --output json --version`
- `statuspage-api-tool --help`

## Auth (informational)

- `statuspage-api-tool auth check`

## Status

- `statuspage-api-tool status get`

## Summary

- `statuspage-api-tool summary get`

## Incidents

- `statuspage-api-tool incidents list`

## Scheduled maintenances

- `statuspage-api-tool maintenances list`

## Example outputs (fixed)

See `docs/examples/outputs/` for sample `--output json` outputs for each command.
