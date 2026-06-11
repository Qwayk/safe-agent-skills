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
shopify-admin-api-tool onboarding
```

3) Smoke test

```bash
shopify-admin-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
shopify-admin-api-tool --output json --version
```

If you want to validate your env file without modifying it, you can point at `.env.example`:

```bash
shopify-admin-api-tool --env-file .env.example auth check
```

4) One representative query (read-only)

```bash
shopify-admin-api-tool --output json query shop
```

Important: query stdout is not redacted. Treat outputs as sensitive, especially when using `--return-shape-file`.

Mutation commands stay preview-first by default. After review, live apply still needs the normal mutation risk flags plus explicit `--ack-no-snapshot` when no operation-specific saved snapshot is available.
