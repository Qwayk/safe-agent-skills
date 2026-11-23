# Proof and verification

## November 23, 2026 local checks

Fresh wheels built from the source and the local release copy. Both clean installs of `skimlinks-safe-cli` passed 26 tests using simulated Skimlinks replies. The local `skimlinks` skill installed into a temporary Codex skills folder and matched all 46 files in the local release copy. Both skill files passed the skill validator, and local guide links passed.

The checks covered a private settings file, keeping shell settings out of the named account file, and hiding credentials and temporary tokens in output and logs. They also covered rejecting bad Product Key inputs before sending a request, showing when a merchant search has another page, and distinguishing an empty report from a failed report. A full destination URL built a local link without opening it.

These are local checks using simulated replies. Product Key access still needs a live lookup.

## June 11, 2026 verification

Last verified: **2026-06-11**

Tool version: `0.1.0`

Validation runs:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .[dev]
.venv/bin/python -m unittest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
git diff --check
```

Results:

```text
Install: OK
Unit tests: Ran 23 tests, OK
Ruff: All checks passed
Mypy: Success, no issues found in 19 source files
Git whitespace check: OK
```

What was verified locally:
- Import coverage for package modules.
- JSON parse errors produce one JSON object.
- Version command works without `.env`.
- Onboarding creates placeholder-only `.env`.
- Auth failure output does not leak secret env values.
- Merchant command passes official filters and default publisher domain ID.
- Reporting link report passes repeated `dim` and `met` params.
- Product Key multi-product command uses product credentials and read-like POST body.
- Product Key commands reject missing `publisher_domain_id` unless `SKIMLINKS_PUBLISHER_DOMAIN_ID` is configured.
- Product Key passes the official `sort_desc` string value `asc` or `desc` instead of a boolean.
- Product Key docs coverage stays synced to the required publisher-domain and sort-direction contract.
- Link Wrapper builds an encoded URL without clicking it.
- README and quickstart opening contract now stay in the public-ready user-first shape.
- Public proof docs and example outputs no longer leak private workspace paths.
- Stale starter-tool terms are absent from the tool folder.

Smoke commands:

```bash
.venv/bin/skimlinks-safe-cli --output json --version
.venv/bin/skimlinks-safe-cli --output json onboarding --no-write-env
.venv/bin/skimlinks-safe-cli --env-file .env.example --output json auth check
.venv/bin/skimlinks-safe-cli --output json link-wrapper build --id 123X456 --url "https://merchant.example/product?sku=abc" --xcust order-789 --sref https://qwayk.example/post
```

Smoke results:
- Version returned `skimlinks-safe-cli` `0.1.0`.
- Onboarding returned setup steps and did not write `.env`.
- Auth check against `.env.example` failed safely because credentials are missing.
- Link Wrapper returned an encoded `go.skimresources.com` URL and did not open it.

Live Skimlinks API calls were not run because no real credentials are stored in this repo.

Example outputs with private values removed:

- [Version](examples/outputs/version.json)
- [Missing account settings](examples/outputs/auth_check_missing_config.json)
- [Missing Product Key publisher domain ID](examples/outputs/product_key_missing_domain_id.json)
- [Built affiliate link](examples/outputs/link_wrapper_build.json)

Main remaining live risk:
- Product Key access may be disabled unless Skimlinks enables separate Product Key credentials.
- Data Pipe and Skimlinks JavaScript are official docs areas, but not HTTP API command families.
