# Proof pack

Note: you don’t need to run these commands yourself. They exist so you or your reviewer can audit behavior and prove what happened.

## Last verified

- Date (UTC): 2026-05-21
- Tool version: 0.1.0
- Provider API version: Hacker News Firebase API v0

## Blessed local validation

Run inside the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

## Smoke commands

- `hacker-news-api-tool --output json --version`
- `hacker-news-api-tool --output json auth check`
- `hacker-news-api-tool --output json stories top`
- `hacker-news-api-tool --output json items get --id 8863`
- `hacker-news-api-tool --output json users get --id pg`
- `hacker-news-api-tool --output json updates get`

## Example outputs

Committed examples live under `docs/examples/outputs/`:
- `version.json`
- `auth_check.json`
- `stories_top.json`
- `item_8863.json`
- `user_pg.json`
- `updates.json`

## What can go wrong

- Wrong API root → verify `auth check` fails cleanly and the error stays JSON-safe.
- Missing item or user → verify the CLI returns `ok=false` and `error_type=ValidationError`.
- Upstream response drift → verify `docs/api_coverage.md`, tests, and committed examples still match.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug notes: `docs/engineering_notes.md`
