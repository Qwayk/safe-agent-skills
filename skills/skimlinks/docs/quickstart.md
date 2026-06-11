# Quickstart

This page is a technical command reference. If you are not technical, start with `use_cases.md` and `onboarding.md`.

## Install Locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## Configure

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

## Smoke Checks

```bash
skimlinks-safe-cli --output json --version
skimlinks-safe-cli onboarding
skimlinks-safe-cli auth check
```

## First Safe Commands

```bash
skimlinks-safe-cli merchant verticals list
skimlinks-safe-cli merchant alternative-verticals list
skimlinks-safe-cli link-wrapper build --url https://merchant.example/product
```

Commands that call private Skimlinks data need credentials and publisher IDs. Link Wrapper only builds a URL and does not click it.
