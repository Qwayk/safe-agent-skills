# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md), [Connect your Microsoft Ads account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the CLI path when you already want exact commands.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and fill your Microsoft Ads values.

If you want the tool to create the starter file for you, run:

```bash
msads-api-tool onboarding
```

Store your OAuth token JSON locally:

```bash
msads-api-tool auth token set --file token.json
```

## 3. Local smoke checks

Version output with no network call:

```bash
msads-api-tool --output json --version
```

Check whether a local OAuth token is already stored:

```bash
msads-api-tool auth token status
```

## 4. First live check

Real network reads still require `--live`:

```bash
msads-api-tool --output json --live auth check
```

## 5. First safe live reads

Review account access:

```bash
msads-api-tool --output json --live customer-management get-accounts-info
```

If you already know the account you want to inspect, review campaigns with a request file:

```bash
msads-api-tool --output json --live campaign-management get-campaigns-by-account-id --request-json request.json
```

## 6. Plan a write-capable action

Write-capable operations start as dry-run plans by default, so save the plan first:

```bash
msads-api-tool --plan-out plan.json campaign-management update-campaigns --request-json request.json
```

Nothing goes live in this step.

## 7. Request apply only after review

After you review `plan.json`, a higher-risk change can need all of these gates:

```bash
msads-api-tool --live --apply --yes --plan-in plan.json --ack-no-snapshot campaign-management update-campaigns --request-json request.json
```

Delete-like actions can also require `--ack-irreversible`.

## 8. Need the full command list?

Use:

- [Command reference](command_reference.md)
- [API coverage](api_coverage.md)
