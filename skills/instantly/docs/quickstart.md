# Quickstart

Use this page when you want the exact Instantly commands.
If you want the simpler path first, start with [What you can do](use_cases.md) and [Connect your Instantly account](onboarding.md).

## 1) Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional dev extras:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure your local `.env`

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
instantly-api-tool onboarding
```

Required fields:

- `INSTANTLY_API_BASE_URL=https://api.instantly.ai/api/v2`
- `INSTANTLY_API_KEY=...`

Never commit `.env`.

## 3) Check auth first

```bash
instantly-api-tool --output json auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
instantly-api-tool --output json --version
```

Note: `auth check` requires a real Instantly API key in `.env`.

## 4) Run safe reads first

Workspace and campaigns:

```bash
instantly-api-tool --output json whoami
instantly-api-tool --output json campaigns list --limit 10
```

Campaign analytics:

```bash
instantly-api-tool --output json analytics campaigns --start-date 2026-06-01 --end-date 2026-06-07
```

## 5) Preview a careful change

Preview a safe campaign activation:

```bash
instantly-api-tool --output json campaigns activate --campaign-id CAMPAIGN_ID
```

Or preview a high-risk lead move from a file:

```bash
instantly-api-tool --output json leads move --file move_leads.json
```

## 6) Apply only after review

Apply a supported campaign activation:

```bash
instantly-api-tool --output json --apply campaigns activate --campaign-id CAMPAIGN_ID
```

Apply a high-risk lead move after review:

```bash
instantly-api-tool --output json --apply --yes leads move --file move_leads.json
```

Some destructive or irreversible applies also need a reviewed `--plan-in` file, and some create, send, or no-pre-read families need explicit no-snapshot approval before HTTP.

## Sensitive reads

Some reads are intentionally stricter because the raw response can contain account internals or secrets.

Example:

```bash
instantly-api-tool --output json accounts list
instantly-api-tool --output json --apply --yes accounts list
```

In those cases stdout stays metadata-only and the full redacted result goes to the receipt or local proof files instead of chat.
