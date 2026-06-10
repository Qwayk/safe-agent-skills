# Quickstart

If you’re non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (minimal)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (contributors): install dev extras:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
unsplash-api-tool onboarding
```

3) Smoke test

```bash
unsplash-api-tool auth check
```

4) Try a read endpoint

```bash
unsplash-api-tool --output json stats total
```

5) Export (deterministic pagination)

Note: `--per-page` is capped at 30, and multi-page exports require `--yes`.

```bash
unsplash-api-tool --output json --yes export photos-list --out export.json --start-page 1 --max-pages 2 --per-page 10
```

If you want a safe machine-readable version output (no `.env` required):

```bash
unsplash-api-tool --output json --version
```
