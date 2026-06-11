# Quickstart

Want the short non-technical path first? Start with [What you can do with TikTok Marketing](use_cases.md), [Connect your TikTok Marketing account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

One important rule first: `auth check` is already a live helper, but the wider `api` surface still needs `--live` for real provider reads.

## 1) Install

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (developer tooling):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure

Run onboarding or copy `.env.example` to `.env`:

```bash
tiktok-marketing-api-tool --output json onboarding
```

Then fill the TikTok values from [Configuration](configuration.md).

## 3) First safe checks

```bash
tiktok-marketing-api-tool --output json --version
tiktok-marketing-api-tool --output json auth check
tiktok-marketing-api-tool --output json api ops list
tiktok-marketing-api-tool --output json api ops show --op oauth2-advertiser-get
```

## 4) First reviewed plan

Create a small query file first, then build the dry-run plan:

```bash
tiktok-marketing-api-tool --output json --plan-out plan.json api campaign-get --query-json query.json
```

## 5) First real API read

The broad `api` surface needs `--live`:

```bash
tiktok-marketing-api-tool --output json --live api campaign-get --query-json query.json
```

## 6) Write planning rules

If you move from reads into live TikTok Marketing changes:

- start with the dry-run plan first
- expect the normal apply flags for write-like operations
- expect explicit no-snapshot approval too when the command cannot save real before-state
- keep the reviewed plan file so the apply step has a clear audit trail
