# Quickstart

Want the short non-technical path first? Start with [What you can do with Mercury](use_cases.md), [Connect your Mercury API token](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

Requires: **Python 3.11+**.

## 1) Install

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional dev extras:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure

Copy `.env.example` to `.env`, then fill:

- `MERCURY_API_TOKEN`
- `MERCURY_API_BASE_URL`

Optional:

- `MERCURY_AUTH_SCHEME`

For a guided first-time setup, run:

```bash
mercury-api-tool onboarding
```

## 3) First safe checks

```bash
mercury-api-tool --output json --version
mercury-api-tool --output json auth check
mercury-api-tool --output json accounts list
```

## 4) Common next commands

Review transactions:

```bash
mercury-api-tool --output json transactions list --limit 20
```

Preview a CSV export without writing a file yet:

```bash
mercury-api-tool --output json export transactions --format csv --out ./transactions.csv
```

Write the export after review:

```bash
mercury-api-tool --output json --apply export transactions --format csv --out ./transactions.csv
```

Download an invoice PDF locally:

```bash
mercury-api-tool --output json --apply invoices download-pdf --invoice-id inv_123 --out ./invoice.pdf
```

## 5) Local file-write rules

Mercury reads are remote read-only, but exports and downloads still write local files.

That means:

- preview first with the dry-run output
- use `--apply` before any local file write
- add `--yes` if you are overwriting an existing file

## 6) Module fallback

If you are not using an editable install, you can run:

```bash
PYTHONPATH=src python3 -m mercury_api_tool --output json auth check
```
