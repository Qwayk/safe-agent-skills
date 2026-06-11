# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
sovrn-safe-cli onboarding
```

3) Smoke test

```bash
sovrn-safe-cli auth check
sovrn-safe-cli commerce campaigns get --search PRIMARY
```

`auth check` confirms the local Sovrn auth layout.
`commerce campaigns get` is a real live Commerce read command and is the simplest shared proof step when you have a valid Commerce secret key.

If you want a safe machine-readable version output (no `.env` required):

```bash
sovrn-safe-cli --output json --version
```

If you want to inspect the current config shape without creating a real `.env` yet, you can point at `.env.example`:

```bash
sovrn-safe-cli --env-file .env.example auth check
```

For the Advertising side, the first live proof step is usually:

```bash
sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction
```
