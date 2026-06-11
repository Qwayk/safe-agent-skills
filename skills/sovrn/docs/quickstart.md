# Quickstart

If you want the non-technical path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the fast technical path for install, setup, and your first safe Sovrn checks.

Requires: **Python 3.12+**.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and fill the Sovrn values you want to use first.

If you want guided setup first, run:

```bash
sovrn-safe-cli onboarding
```

## 3. Run safe first checks

Start with a no-credential version check:

```bash
sovrn-safe-cli --output json --version
```

Then check local readiness:

```bash
sovrn-safe-cli auth check
```

`auth check` confirms the local Sovrn auth layout only. It is not live vendor proof.

When your Commerce secret key is ready, the cleanest shared live proof step is:

```bash
sovrn-safe-cli commerce campaigns get --search PRIMARY
```

`commerce campaigns get` is a real live Commerce read command and is the cleanest first proof step when you have a valid Commerce secret key.

For the Advertising side, the first live proof step is usually:

```bash
sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction
```

If you want to inspect the current config shape without creating a real `.env` yet, you can point the tool at `.env.example`:

```bash
sovrn-safe-cli --env-file .env.example auth check
```
