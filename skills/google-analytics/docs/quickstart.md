# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md), [Connect your Google Analytics access](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the CLI path when you already want exact commands.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and fill your values.

If you want the tool to create the starter file for you, run:

```bash
ga4-api-tool onboarding
```

## 3. Smoke test

```bash
ga4-api-tool auth check
```

If you want a safe machine-readable version output with no `.env` file:

```bash
ga4-api-tool --output json --version
```

If you want to confirm the network-backed auth path too, run:

```bash
ga4-api-tool --apply auth check
```

## 4. First safe reads

List the accounts and properties you can access:

```bash
ga4-api-tool admin v1alpha account-summaries list
```

Example report command shape:

```bash
ga4-api-tool --env-file .env data v1beta properties run-report --property properties/123
```

## 5. Plan a write-capable change

Write-capable GA4 admin commands start as dry-run plans by default:

```bash
ga4-api-tool --env-file .env admin v1alpha accounts patch --name accounts/123 --body-json '{}'
```

## 6. Request apply only after review

When no useful before-state can be saved, GA4 write apply needs explicit no-snapshot approval:

```bash
ga4-api-tool --env-file .env --apply --ack-no-snapshot admin v1alpha accounts patch --name accounts/123 --body-json '{}'
```

Higher-risk writes can also require `--yes`, `--plan-in`, or `--ack-irreversible` depending on the command and risk level.

## 7. Need the full command list?

Use:

- [Command reference](command_reference.md)
- [All generated commands](official_commands.txt)
