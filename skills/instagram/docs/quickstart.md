# Instagram Login Tool Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is the short technical setup path.

1) Create a local venv and install the tool

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

2) Create `.env`

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
instagram-api-tool onboarding
```

3) Build the Instagram Login consent URL

```bash
instagram-api-tool auth login-url --scope instagram_business_basic
```

4) Add access token state

Auth write helpers create plans. When the tool cannot save useful old token state, apply requires explicit no-snapshot approval before token exchange or local token writes. For reads today, you can also put a valid `INSTAGRAM_ACCESS_TOKEN` in `.env` yourself and keep it out of chat.

5) Smoke test the connection

```bash
instagram-api-tool auth check
```

6) Try one read command

```bash
instagram-api-tool users me --fields user_id,username,account_type
```

7) Try one safe write preview

```bash
instagram-api-tool media publish --ig-user-id 17841400000000000 --creation-id 17890000000000000
```

That last command creates a dry-run plan. If you add `--apply --yes`, the tool requires explicit no-snapshot approval before Instagram HTTP when no saved snapshot is available.

Version output still works without `.env`:

```bash
instagram-api-tool --output json --version
```
