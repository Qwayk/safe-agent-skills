# Quickstart

If you want the human path first, start with [What you can do with Meta Ads](use_cases.md), [Connect your Meta Ads account](onboarding.md), and [How this skill stays safe](safety_model.md).

## 1) Install (editable)

From this folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## 2) Create `.env`

```bash
cp .env.example .env
```

Fill in `META_ADS_ACCESS_TOKEN` (and optionally `META_ADS_AD_ACCOUNT_ID`).

## 3) Smoke test

```bash
meta-ads-api-tool --output json --version
meta-ads-api-tool onboarding
meta-ads-api-tool --output json auth check
```

## 4) First useful commands

```bash
meta-ads-api-tool --output json ad-accounts list --fields id,name
meta-ads-api-tool --output json --ad-account-id act_<id> campaigns list --fields id,name,status
meta-ads-api-tool --output json --ad-account-id act_<id> insights get --level campaign --fields campaign_id,impressions,clicks,spend --since 2026-01-01 --until 2026-01-31
meta-ads-api-tool --output json presets list
meta-ads-api-tool --output json snapshot export --ad-account-id act_<id> --preset ecom_core --since 2026-01-01 --until 2026-01-31 --out-dir ./exports --max-pages 2
meta-ads-api-tool --output json insights compare --ad-account-id act_<id> --level ad --fields ad_id,impressions,clicks,spend --since-a 2026-01-01 --until-a 2026-01-07 --since-b 2026-01-08 --until-b 2026-01-14
meta-ads-api-tool --output json creatives anatomy --creative-id <creative_id>
meta-ads-api-tool --output json previews get --creative-id <creative_id> --ad-format DESKTOP_FEED_STANDARD
```

This page is the technical reference for install, setup, auth checks, and first Meta Ads commands.
