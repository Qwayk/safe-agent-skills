# Quickstart

If you want the plain-English path first, start with [What you can do with Statuspage](use_cases.md), [Use a public Statuspage URL](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the shortest direct CLI path for this read-only skill.

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

`auth check` is informational only here. It confirms that this skill does not need credentials for the normal public-page flow.

## Version

```bash
statuspage-api-tool --output json --version
```
