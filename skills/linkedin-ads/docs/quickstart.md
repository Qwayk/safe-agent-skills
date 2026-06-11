# Quickstart

If you want the human path first, start with [What you can do with LinkedIn Ads](use_cases.md), [Connect your LinkedIn Ads account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the technical reference for install, setup, approval checks, and first LinkedIn Ads commands.

## 1) Install

From the tool folder:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## 2) Put config in place

```bash
cp .env.example .env
```

Then fill `LINKEDIN_ADS_TOKEN` in `.env` or run:

```bash
linkedin-ads-api-tool onboarding
```

`onboarding` creates a placeholder `.env` with `LINKEDIN_ADS_TOKEN` when missing.
You can also use `LINKEDIN_ADS_ACCESS_TOKEN` or `LINKEDIN_ADS_API_TOKEN` instead.

## 3) Confirm approval flow

```bash
linkedin-ads-api-tool --output json auth check
```

This is a safe live GET for `GET /adAccountUsers?q=authenticatedUser`.
It confirms the token loads and that LinkedIn can authenticate your user in this app context.

## 4) Start with safe first commands

Read commands are live and do not need `--apply`:

```bash
linkedin-ads-api-tool --output json ad-account-users list-authenticated-user
linkedin-ads-api-tool --output json ad-campaigns search --ad-account-id 123456
```

## 5) Test write safety

Write commands can run first in plan mode. Use a plan file first:

```bash
linkedin-ads-api-tool \
  --output json \
  --plan-out .state/plan.json \
  ad-accounts create \
  --body-json '{"name":"Sample account"}'
```

Then apply only after review:

```bash
linkedin-ads-api-tool --output json --apply --ack-irreversible ad-accounts create --body-json '{"name":"Sample account"}'
```

If you do not have a token, dry-run plans still work for non-read operations, but live LinkedIn reads will not.

## 6) Helpful next references

- [Command reference](command_reference.md)
- [Authentication details](authentication.md)
- [API coverage](api_coverage.md)
