# Quickstart

Want the short non-technical path first? Start with [What you can do with X](use_cases.md), [Connect your X account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the fast technical path for setup, first safe checks, and your first real X queries.

Requires: **Python 3.12+**.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env`, then fill:

- `X_API_BASE_URL=https://api.x.com/2`
- one auth option to start:
  - app bearer token for many reads, or
  - OAuth user setup for user-context reads, DMs, and most writes

If you want guided setup first, run:

```bash
x-api-tool onboarding
```

## 3. First safe checks

Start with the no-credential version check:

```bash
x-api-tool --output json --version
```

Then run the local auth check:

```bash
x-api-tool --env-file .env auth check
```

List the pinned X operation inventory:

```bash
x-api-tool --output json api ops list
```

If you want to run without creating a real `.env` yet, you can point at `.env.example`:

```bash
x-api-tool --env-file .env.example auth check
```

## 4. First live reads

When your token is ready, the cleanest first live checks are usually:

```bash
x-api-tool --live auth check
x-api-tool --live users resolve --username jack
```

## 5. First safe write plan

When you want to preview a write without sending it yet:

```bash
x-api-tool dm send --to-user-id 123 --message "hi"
```

That creates a dry-run plan first. Live writes need the extra approval flags described in [How this skill stays safe](safety_model.md).
