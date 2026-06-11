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

If `QDRANT_CLOUD_API_KEY` contains shell-special characters such as `|`, quote it:

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

Tip: for a guided first-time setup, run:

```bash
qdrant-cloud-api-tool onboarding
```

3) Smoke test

```bash
qdrant-cloud-api-tool --env-file .env --output json auth check
qdrant-cloud-api-tool --env-file .env --output json --live auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
qdrant-cloud-api-tool --output json --version
```

If you want to run the template without creating a real `.env` yet, you can point at `.env.example`:

```bash
qdrant-cloud-api-tool --env-file .env.example --output json auth check
```

If your real env file lives elsewhere, point to it explicitly:

```bash
qdrant-cloud-api-tool --env-file /full/path/to/.env --output json --live auth check
```
