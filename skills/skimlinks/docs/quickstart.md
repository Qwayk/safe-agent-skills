# Quickstart

Want the short non-technical path first? Start with [What you can do with Skimlinks](use_cases.md), [Connect your Skimlinks account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

Requires: **Python 3.12+**.

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

```bash
cp .env.example .env
```

Fill `.env` locally. Do not paste secrets into chat.

Required for Merchant API and Reporting API:
- `SKIMLINKS_CLIENT_ID`
- `SKIMLINKS_CLIENT_SECRET`
- `SKIMLINKS_PUBLISHER_ID`

Required for Product Key unless passed per command:
- `SKIMLINKS_PUBLISHER_DOMAIN_ID`

Optional for Link Wrapper defaults and Product Key credential split:
- `SKIMLINKS_LINK_WRAPPER_ID`
- `SKIMLINKS_PRODUCT_CLIENT_ID`
- `SKIMLINKS_PRODUCT_CLIENT_SECRET`

For a guided first-time setup, run:

```bash
skimlinks-safe-cli onboarding
```

## 3) First safe checks

```bash
skimlinks-safe-cli --output json --version
skimlinks-safe-cli onboarding
skimlinks-safe-cli auth check
```

If you plan to use Product Key, check that path separately too:

```bash
skimlinks-safe-cli auth check --scope product
```

## 4) Common next commands

Review active merchants:

```bash
skimlinks-safe-cli merchant merchants list --search laptop --country US --limit 10
```

Review top commission links:

```bash
skimlinks-safe-cli reporting link-report query --start-date 2026-01-01 --end-date 2026-01-31 --dim merchant_id --met clicks
```

Check Product Key alternatives:

```bash
skimlinks-safe-cli product-key product get --publisher-domain-id 456 --product-url https://merchant.example/product --sort-by epc --sort-desc desc
```

Build a Link Wrapper URL locally:

```bash
skimlinks-safe-cli link-wrapper build --url https://merchant.example/product
```

## 5) Read-only rules

This skill does not change anything inside Skimlinks.

That means:

- Merchant, Reporting, and Product Key calls only read or query data
- Link Wrapper only builds a URL locally
- onboarding can create a placeholder `.env`, but it does not fill secrets for you

## 6) Module fallback

If you are not using an editable install, you can run:

```bash
PYTHONPATH=src python3 -m skimlinks_safe_agent_cli --output json auth check
```
