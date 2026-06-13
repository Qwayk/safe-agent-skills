# Connect your Unsplash account

Unsplash needs a local access key before an agent can search photos, inspect creators, review license data, or prepare downloads.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a photo search and preview links before saving files or choosing final images.

## What you need

- `UNSPLASH_ACCESS_KEY`
- the default Unsplash API base URL unless you intentionally changed it
- a local output path only when you want exports or downloads written to your machine

## Step 1. Create the local `.env` file

The easiest path is one of these:

1. run `unsplash-api-tool --output json onboarding`
2. or copy `.env.example` to `.env`

Then fill:

- `UNSPLASH_API_BASE_URL=https://api.unsplash.com`
- `UNSPLASH_ACCESS_KEY`

## Step 2. Run the first safe checks

These are the best first commands:

```bash
unsplash-api-tool --output json --version
unsplash-api-tool --output json auth check
unsplash-api-tool --output json photos search --query "minimal home office" --per-page 3
unsplash-api-tool --output json stats total
```

## What to ask your agent next

- "Can you confirm the Unsplash skill is connected and build a shortlist for my topic?"
- "Can you show me the safest first export or research pull before we plan any downloads?"
- "Can you plan downloading these approved photo IDs without applying yet?"

## If something fails

The most common causes are:

- missing or invalid Access Key
- rate limits
- a search or filter that does not match real Unsplash data

Use [Troubleshooting](troubleshooting.md) if the auth check or the first search fails.
