# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md), [Connect your Google Business Profile access](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the CLI path when you already want exact commands.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and add your Google OAuth client secrets path.

If you want the tool to create or refresh the starter file for you, run:

```bash
google-business-profile-safe-cli onboarding
```

## 3. Sign in and smoke test

```bash
google-business-profile-safe-cli auth login --console
google-business-profile-safe-cli auth check
```

If you want a safe machine-readable version output with no `.env` file:

```bash
google-business-profile-safe-cli --output json --version
```

## 4. First safe reads

List the accounts you can access:

```bash
google-business-profile-safe-cli account-management accounts list
```

List locations from one account:

```bash
google-business-profile-safe-cli business-info accounts locations list --parent accounts/123 --read-mask "title,primaryPhone"
```

Check one location in more detail:

```bash
google-business-profile-safe-cli business-info locations get --name locations/abc --read-mask "name,title,storeCode"
```

## 5. Plan a write-capable change

Write-capable actions start as dry-run plans by default:

```bash
google-business-profile-safe-cli \
  --plan-out /tmp/location.patch.plan.json \
  business-info locations patch \
  --name locations/abc \
  --update-mask title,storeCode \
  --location-file /path/to/location.json
```

## 6. Request apply only after review

Many Google Business Profile writes require a reviewed plan file first:

```bash
google-business-profile-safe-cli --apply \
  --plan-in /tmp/location.patch.plan.json \
  --receipt-out /tmp/location.patch.receipt.json \
  business-info locations patch \
  --name locations/abc \
  --update-mask title,storeCode \
  --location-file /path/to/location.json
```

If the write has no saved before-state, apply also needs `--ack-no-snapshot`.
Higher-risk actions can also require `--yes` or `--ack-irreversible`.

## 7. Need the full command list?

Use:

- [Command reference](command_reference.md)
- [Browse all docs](README.md)
