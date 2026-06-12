# Amazon Product Advertising API

**Capability:** Read-only

Amazon Product Advertising API is useful when affiliate research needs real catalog data instead of copied product-page guesses. It can help an agent search products, resolve ASINs, check browse nodes, fetch product details, and build clean affiliate links from the items you already want to compare.

It is a good fit for jobs like niche research, gift-guide shortlists, product comparison tables, Amazon URL cleanup, affiliate link generation, category checks, and repeatable spreadsheet-driven product pulls.

The tool is read-only against Amazon. It cannot create, edit, or delete Amazon products or account data. The thing to watch is scope: wrong marketplace settings, wasted API requests, or a batch that is larger than you meant to run.

A good first ask is: "Check the Amazon Product Advertising skill is configured, search for five products in my niche, resolve the ASINs, and build clean affiliate links for the best matches."

## Start here first

- Want ideas for real Amazon research work? [What you can do with Amazon Product Advertising API](docs/use_cases.md)
- Need setup? [Connect your Amazon Associates credentials](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Search Amazon products by keyword for research, shortlist building, and content planning.
- Fetch product details for known ASINs.
- Resolve Amazon product URLs into clean ASINs before you reuse them.
- Build affiliate links from known ASINs.
- Check browse nodes and category IDs.
- Run CSV batch jobs for repeated research pulls.

## What access this skill needs

- An Amazon Product Advertising API access key ID.
- An Amazon Product Advertising API secret access key.
- Your Amazon Associates partner tag.
- The right host, region, and marketplace for the Amazon store you want to query.

## Install and first run

Install slug: `amazon-paapi-v5`

Ask your agent to install the `amazon-paapi-v5` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@amazon-paapi-v5 -g -y
```

Then try a safe first ask like:

```text
Check the Amazon Product Advertising skill is configured, search for 5 products related to cast iron skillets, and build clean affiliate links for the best matches.
```

## How this skill stays safe

- It is read-only to Amazon by design.
- It refuses remote writes. `--apply` exists only for cross-tool consistency and does not enable Amazon writes here.
- Large multi-request fetches still need `--yes`, so a big batch does not run by accident.
- Commands keep machine-readable JSON output and avoid printing secrets.
- Docs, tests, examples, proof files, and API coverage all live in this repo.

## What it covers today

This skill covers:

- `auth check`
- `product search`
- `product get`
- `product variations`
- `product resolve`
- `link build`
- `browse get`
- `jobs run` for CSV-based research batches

## What happens before a real change

This skill does not change anything in Amazon. It reads product and browse data and returns structured output that you can review or save locally.

## What proof it leaves behind

- Commands return machine-readable JSON that you can save or review.
- Batch jobs return one summary JSON object so it is clear what ran and what failed.
- The proof pack includes redacted example outputs for the main command shapes.
- The docs, tests, and API coverage ledger are all in this repo.

## Limits

- No creates, updates, deletes, or other remote Amazon writes.
- Live reads still need valid PA-API credentials and a real Associates setup.
- Region, host, or marketplace mismatches can still block otherwise valid requests.
- Larger multi-request reads may need `--yes` before they run.

## Helpful docs

- [Browse all Amazon Product Advertising docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Jobs and batch guide](docs/jobs_and_batches.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
