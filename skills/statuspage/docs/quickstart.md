# Quickstart

If you are non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is the shortest direct CLI path for this read-only tool.

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## Smallest first run

```bash
statuspage-api-tool --output json --base-url https://status.atlassian.com status get
```

## Optional repeat setup with `.env`

If you do not want to repeat `--base-url` every time:

1. Copy `.env.example` to `.env`.
2. Set `STATUSPAGE_BASE_URL=https://status.atlassian.com`.

Then you can run:

```bash
statuspage-api-tool --output json status get
```

## Auth check (no API call)

```bash
statuspage-api-tool --output json auth check
```

## Version

```bash
statuspage-api-tool --output json --version
```
