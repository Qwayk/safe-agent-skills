# Quickstart

If you’re non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (minimal)

```bash
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install -e .
```

Optional (dev extras):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values (do not commit `.env`).

If your Plausible base URL is protected by Cloudflare Access, also set:
- `CF_ACCESS_CLIENT_ID`
- `CF_ACCESS_CLIENT_SECRET`

3) Smoke test

```bash
python3 -m plausible_api_tool --env-file .env auth check
```

4) Read a quick goals report:

```bash
python3 -m plausible_api_tool --env-file .env stats goals list --date-range 30d --limit 25
```

5) Optional: copy the project playbook template into your project folder:
- `docs/project_playbook_template.md`

## Useful read-only shortcuts

- `python3 -m plausible_api_tool --env-file .env report weekly --days 7 --limit 50`
- `python3 -m plausible_api_tool --env-file .env stats pages top --metric pageviews --days 30 --limit 50`

## Optional: send a test event (writes analytics)

Only do this when you explicitly want to write test data.

```bash
PYTHONPATH=src python3 -m plausible_api_tool --env-file .env --apply --yes --ack-irreversible event send \\
  --name "__plausible_api_tool_test" \\
  --url "https://example.com/__plausible_api_tool_test/$(date +%s)" \\
  --verify
```
