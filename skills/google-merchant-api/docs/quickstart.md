# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md), [Connect your Google Merchant Center account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the CLI path when you already want exact commands.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and fill your Merchant values.

If you want the tool to create the starter file for you, run:

```bash
google-merchant-api-tool onboarding
```

## 3. Local smoke checks

Version output with no Merchant request:

```bash
google-merchant-api-tool --output json --version
```

Check your configured auth mode:

```bash
google-merchant-api-tool --output json auth check
```

## 4. First safe reads

List Merchant accounts:

```bash
google-merchant-api-tool --output json accounts list
```

If you already know the Merchant account you want to inspect, list products:

```bash
google-merchant-api-tool --output json accounts products list --parent accounts/123456
```

## 5. Plan a write-capable action

Write-capable operations start as dry-run plans by default, so save the plan first:

```bash
google-merchant-api-tool --output json --plan-out plan.json accounts product-inputs insert --parent accounts/123456 --body-file product.json
```

Nothing goes live in this step.

## 6. Request apply only after review

After you review `plan.json`, a medium Merchant write can still need explicit no-snapshot approval:

```bash
google-merchant-api-tool --output json --apply --ack-no-snapshot accounts product-inputs insert --parent accounts/123456 --body-file product.json
```

Higher-risk or irreversible writes can also require `--yes --plan-in reviewed-plan.json`, and `DELETE` applies can also require `--ack-irreversible`.

## 7. Need the full command list?

Use:

- [Command reference](command_reference.md)
- [API coverage](api_coverage.md)
