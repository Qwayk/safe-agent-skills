# Command reference

Use this page when you need the exact Amazon PA-API v5 command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Auth

- `amazon-pa-api-tool auth check`

## Product

- `amazon-pa-api-tool product search --query "air fryer" [--search-index All] [--limit 10] [--item-page 1]`
- `amazon-pa-api-tool product get --asin B000000000 [--asin B000000001 ...] [--batch-size 10] [--max-requests 10] [--yes]`
- `amazon-pa-api-tool product variations --asin B000000000 [--variation-page 1] [--variation-count 10]`
- `amazon-pa-api-tool product resolve --url "https://www.amazon.com/dp/B000000000/"`

Tip: add `--include-raw` to include the full PA-API JSON response (default is simplified output).

### Resources (product + browse)

Some PA-API operations accept a `Resources` list to control which fields are returned.

- `--resources-preset basic|none`
- `--resource <ResourceName>` (repeatable; appended to the preset deterministically)

## Links

- `amazon-pa-api-tool link build --asin B000000000`

## Browse

- `amazon-pa-api-tool browse get --browse-node-id 3040 [--browse-node-id 3045 ...] [--batch-size 10] [--max-requests 10] [--yes]`

## Jobs

- `amazon-pa-api-tool jobs run --file jobs.csv [--limit N]`
