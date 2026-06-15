# Safety model

Amazon Product Advertising API is safest when you treat the agent as a focused reader for product lookup and browse-node research. It can help with research and reporting, but it should not be used as proof until it has fetched the actual records behind the summary.

The main safety job is simple: stay inside the supported read surface, keep any saved output private when it contains business data, and avoid broad conclusions from thin list results.

A good safety ask is: "Look up one product or browse node first, then summarize only from the returned product data."

## Core safety rules

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

1. Run `auth check`.
2. Run one small sample search or one known ASIN lookup.
3. Confirm the marketplace and results look right.
4. Expand to bigger batches only after the sample result is correct.

## Proof and review

- Save JSON output when you want a review trail.
- Use `docs/proof.md` for verified command shapes and example outputs.
- Use `docs/api_coverage.md` when you want to inspect what the tool covers today.
