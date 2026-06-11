# Safety model

This tool is intentionally read-only against Amazon Product Advertising API.

## What this tool will never do

- Create, edit, or delete anything in Amazon
- Turn `--apply` into a remote Amazon write
- Print secrets into stdout, stderr, or logs

## What this tool does safely

- Read product, browse, and link-building data from Amazon Product Advertising API
- Resolve Amazon URLs into ASINs without scraping guesses
- Stop batch jobs on the first error so bad rows do not hide inside a long run
- Return exactly one JSON object in `--output json` mode

## Large-read guard

This tool is read-only, but large requests can still waste quota or pull more data than you intended.

For that reason:

- multi-request reads need `--yes`
- the safest path is to start with one small query or one ASIN first
- batch jobs stay strict and stop on the first error

## How to use it safely with an AI agent

Recommended workflow:

1. Run `auth check`.
2. Run one small sample search or one known ASIN lookup.
3. Confirm the marketplace and results look right.
4. Expand to bigger batches only after the sample result is correct.

## Proof and review

- Save JSON output when you want a review trail.
- Use `docs/proof.md` for verified command shapes and example outputs.
- Use `docs/api_coverage.md` when you want to inspect what the tool covers today.
