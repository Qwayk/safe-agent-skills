# What we tested

## November 23, 2026 local checks

Fresh installs of both copies passed 58 offline tests, Ruff, and mypy. From an empty folder, setup created a private settings file and printed the command that uses it. That command found the test token and the installed tool read a simulated stats page.

Using fake replies, the tests checked a changed token, an older preview without a token, a refused request, a missing domain in the reply, and a lost reply. They confirmed the receipt was saved before sending and the same approval could send only once. All 21 guide links and five JSON examples worked in each copy. Both the wheel and the source archive include the skill instructions.

## August 11, 2026 checks

The original `0.1.0` build passed 52 tests, Ruff, mypy, and packaging checks. The tests covered dates, token handling, domain validation, repeated names, the 100-name limit, approved plans, and redirect refusal. The builder checked the installed wheel from outside the checkout and confirmed that the settings file and plan had mode `0600`.

The independent review made one authorized live stats request with the installed wheel. It asked for August 10, 2026, with `page=1` and `page_size=1`. GiantPanda returned HTTP 200. The top-level fields were `end_date`, `pagination`, `start_date`, and `stats`. The live proof covers that stats read. The domain-add checks used simulated replies.

### Original build and archive checks

- `./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` (52 tests)
- `./.venv/bin/python -m ruff check .` (passed)
- `./.venv/bin/python -m mypy src tests` (passed)
- `./.venv/bin/python -m build --outdir dist` (built both archives)
- `dist/giantpanda-0.1.0.tar.gz` SHA-256 `4a5834384798171c949782814d3b3bd91556aefb5e4442b50ff06c33729d6068`
- `dist/giantpanda-0.1.0-py3-none-any.whl` SHA-256 `c14a17e9356e0d053bf0b5bbf5a31c1378662985a25be93ad8935db971aaa041`

The original scans checked the archives and project files for secrets, private paths, stray local files, and trailing whitespace. This was the original installed-wheel check.

```bash
GIANTPANDA_TEST_PYTHON=<configured-python-3.12-or-newer>; \
tmp_root="$(mktemp -d /tmp/giantpanda-final-verify.XXXXXX)"; \
"$GIANTPANDA_TEST_PYTHON" -m venv "$tmp_root/venv"; \
"$tmp_root/venv/bin/pip" install -q "$(pwd)/dist/giantpanda-0.1.0-py3-none-any.whl"; \
install -m 600 .env.example "$tmp_root/auth.env"; \
env -u PYTHONPATH "$tmp_root/venv/bin/giantpanda" --output json --version; \
env -u PYTHONPATH "$tmp_root/venv/bin/giantpanda" --output json --env-file "$tmp_root/auth.env" auth check; \
env -u PYTHONPATH "$tmp_root/venv/bin/giantpanda" --output json --env-file "$tmp_root/auth.env" domains add --dry-run --plan-out "$tmp_root/domains-plan.json" --domain Example.com --domain example.net; \
stat -f '%Lp' "$tmp_root/auth.env" "$tmp_root/domains-plan.json"  # both confirmed 600
```
