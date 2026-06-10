# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

Note: if `cloudflare-api-tool` is not on your PATH, use `python3 -m cloudflare_api_tool ...` (it works from a source checkout and inside a venv).

## 1) Install (recommended)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## 2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
cloudflare-api-tool --output json onboarding
```

Or, if you just want the tool to create the env file placeholders for you (no secrets):

```bash
cloudflare-api-tool --output json config init
cloudflare-api-tool --output json config check
```

## 3) Smoke test

```bash
cloudflare-api-tool --output json auth check
```

If a command feels “hung” on a slow endpoint (commonly Zero Trust), try:

```bash
cloudflare-api-tool --output json --progress --timeout-profile slow auth doctor
```

If you want a safe machine-readable version output (no `.env` required):

```bash
cloudflare-api-tool --output json --version
```

If you want to run directly from a source checkout (no install), you can use:

```bash
python3 -m cloudflare_api_tool --output json --version
python3 -m cloudflare_api_tool --env-file .env --output json auth check
```
