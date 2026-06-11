# Quickstart

Want the short non-technical path first? Start with [What you can do with Amazon Product Advertising API](use_cases.md), [Connect your Amazon Associates credentials](onboarding.md), and [How this skill stays safe](safety_model.md).

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

Copy `.env.example` to `.env`, then fill:

- `AMAZON_PA_ACCESS_KEY_ID`
- `AMAZON_PA_SECRET_ACCESS_KEY`
- `AMAZON_PA_PARTNER_TAG`

If you are not using Amazon US, also update:

- `AMAZON_PA_HOST`
- `AMAZON_PA_REGION`
- `AMAZON_PA_MARKETPLACE`

## 3) First safe checks

```bash
amazon-pa-api-tool --output json --version
amazon-pa-api-tool --output json auth check
amazon-pa-api-tool --output json product search --query "cast iron skillet" --limit 3
```

## 4) Common next commands

Fetch known ASIN details:

```bash
amazon-pa-api-tool --output json product get --asin B000000000
```

Build an affiliate link:

```bash
amazon-pa-api-tool --output json link build --asin B000000000
```

Resolve an Amazon URL into an ASIN:

```bash
amazon-pa-api-tool --output json product resolve --url "https://www.amazon.com/dp/B000000000/"
```

Run a CSV batch job:

```bash
amazon-pa-api-tool --output json jobs run --file jobs.csv
```

## 5) Large read guard

Some multi-ID reads can expand into multiple PA-API requests. When that happens, the tool requires `--yes` before it runs the larger request set.

## 6) Module fallback

If you are not using an editable install, you can run:

```bash
PYTHONPATH=src python3 -m amazon_pa_api_tool --output json auth check
```
