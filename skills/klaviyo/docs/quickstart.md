# Quickstart

Use this page when you want the exact Klaviyo commands.
If you want the simpler path first, start with [What you can do with Klaviyo](use_cases.md) and [Connect your Klaviyo account](onboarding.md).

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

```bash
cp .env.example .env
```

Tip: for guided first-time setup, run:

```bash
klaviyo-safe-agent-cli onboarding
```

Required fields:

- `KLAVIYO_API_BASE_URL=https://a.klaviyo.com`
- `KLAVIYO_API_KEY=...`
- `KLAVIYO_COMPANY_ID=...` only for `/client/*` calls

Never commit `.env`.

## 3) Check auth first

```bash
klaviyo-safe-agent-cli --output json auth check
```

If you want a safe machine-readable version output with no `.env` needed:

```bash
klaviyo-safe-agent-cli --output json --version
```

## 4) Discover the exact operation

```bash
klaviyo-safe-agent-cli --output json api ops list --method GET
```

Show one operation with its method, path, and requirements:

```bash
klaviyo-safe-agent-cli --output json api ops show --op get_accounts
```

## 5) Run safe reads first

Reads need `--live`. Without `--live`, the tool only returns a dry-run plan.

Account and campaign checks:

```bash
klaviyo-safe-agent-cli --output json --live api get_accounts
klaviyo-safe-agent-cli --output json --live api get_campaigns
```

Audience and profile checks:

```bash
klaviyo-safe-agent-cli --output json --live api get_lists
klaviyo-safe-agent-cli --output json --live api get_profiles --query 'page[size]=5'
```

## 6) Preview a careful change

Plan a low-risk write first:

```bash
klaviyo-safe-agent-cli --output json --plan-out plan.json api create_coupon --body-json coupon.json
```

Plan a high-impact audience change first:

```bash
klaviyo-safe-agent-cli --output json --plan-out bulk_plan.json api bulk_suppress_profiles --body-json suppress.json
```

## 7) Apply only after review

Apply a reviewed low-risk write:

```bash
klaviyo-safe-agent-cli --output json --live --apply --ack-no-snapshot api create_coupon --body-json coupon.json
```

Apply a reviewed high-impact write:

```bash
klaviyo-safe-agent-cli --output json --live --apply --yes --plan-in bulk_plan.json --ack-no-snapshot api bulk_suppress_profiles --body-json suppress.json
```

Current Klaviyo write families do not save before-state snapshots, so approved live writes need explicit `--ack-no-snapshot`.
