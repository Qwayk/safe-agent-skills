# Quickstart

Start here for the first safe NameBright check.

## Install for local use

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Add your account settings

Copy `.env.example` to `.env` and fill:
- `NAMEBRIGHT_CLIENT_ID`
- `NAMEBRIGHT_CLIENT_SECRET`
- `NAMEBRIGHT_TIMEOUT_S` (optional)

## Onboard once

```bash
namebright-safe-cli onboarding
```

## First account check

```bash
namebright-safe-cli --output json auth check
```

## First useful read

```bash
namebright-safe-cli --output json account show
namebright-safe-cli --output json domains list --domains-per-page 5
```

## Version

```bash
namebright-safe-cli --output json --version
```

If `auth check` succeeds, move to the command guide for the operation you need.
