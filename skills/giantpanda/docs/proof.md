# Proof and verification

This page records what was checked and what still needs real provider proof.

## Last verified

- Date (UTC): **2026-08-11**
- Verified by: `giantpanda-builder` for local and installed-wheel checks; independent governor for the one provider-live stats read
- Tool version: `0.1.0`
- Base URL: `https://account.giantpanda.com`

## What this proves

- Parser returns one JSON object in `--output json`.
- Command flags and safety gates match the written docs.
- Read command and write-plan/apply flow match explicit tests for:
  - date parsing and window checks,
  - auth readiness and missing-token behavior,
  - add-domain normalization, dedupe, exact plan binding, and required apply gates,
  - provider-response verification paths and receipt handling,
  - redirect refusal before any follow-up request,
  - no token or auth header leaks in outputs or logs.

## Local/mock checks run (exact list)

- `./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` (52 tests)
- `./.venv/bin/python -m ruff check .` (0 issues)
- `./.venv/bin/python -m mypy src tests` (0 issues)
- `./.venv/bin/python -m build --outdir dist` (builds:
  - `dist/giantpanda-0.1.0.tar.gz`
  - `dist/giantpanda-0.1.0-py3-none-any.whl`)
- SHA-256:
  - sdist: `4a5834384798171c949782814d3b3bd91556aefb5e4442b50ff06c33729d6068`
  - wheel: `c14a17e9356e0d053bf0b5bbf5a31c1378662985a25be93ad8935db971aaa041`
- Installed package check run in a clean venv outside source (no source-tree `PYTHONPATH`):
- `GIANTPANDA_TEST_PYTHON=<configured-python-3.12-or-newer>; \
  tmp_root="$(mktemp -d /tmp/giantpanda-final-verify.XXXXXX)"; \
  "$GIANTPANDA_TEST_PYTHON" -m venv "$tmp_root/venv"; \
  "$tmp_root/venv/bin/pip" install -q "$(pwd)/dist/giantpanda-0.1.0-py3-none-any.whl"; \
  install -m 600 .env.example "$tmp_root/auth.env"; \
  env -u PYTHONPATH "$tmp_root/venv/bin/giantpanda" --output json --version; \
  env -u PYTHONPATH "$tmp_root/venv/bin/giantpanda" --output json --env-file "$tmp_root/auth.env" auth check; \
  env -u PYTHONPATH "$tmp_root/venv/bin/giantpanda" --output json --env-file "$tmp_root/auth.env" domains add --dry-run --plan-out "$tmp_root/domains-plan.json" --domain Example.com --domain example.net; \
  stat -f '%Lp' "$tmp_root/auth.env" "$tmp_root/domains-plan.json"  # both confirmed 600`
- Focused artifact scan checks for:
  - `dist/` archive names and contents (for `.env`, `.state`, `.venv`, `.pyc`, cache, private paths, tokens/secret keys)
  - source-tree link/path/private scans in `src`, `tests`, `docs`
- Focused trailing-whitespace scan across the untracked tool source and docs (0 findings)

## Provider-live stats proof

- On 2026-08-11, the independent governor ran exactly one installed-wheel request to `GET /api/v1/domains/stats/` at the fixed production host.
- Query: `start_date=2026-08-10`, `end_date=2026-08-10`, `page=1`, `page_size=1`.
- The CLI exited `0` with `ok: true` and HTTP `200`.
- The provider JSON was an object with these top-level keys: `end_date, pagination, start_date, stats`.
- Exactly one provider request was made, with no retry.
- The token, domains, revenue, and raw provider response were not printed or saved.

## Live-write limit

- No live `domains add` has been sent.
- The builder made no provider request. The only provider-live proof is the governor-owned stats read recorded above.
- Provider behavior and account effects for `domains add` remain local and mocked only.
- The installed-wheel dry-run plan path was explicitly written to temp path and confirmed mode `0600`.
