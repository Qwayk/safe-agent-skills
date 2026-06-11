# Connect your Amazon Associates credentials

Use this page when you want the shortest safe setup path for Amazon Product Advertising API work.

This skill runs on your machine and uses credentials you store locally. You do not need to write code, but you do need real Amazon Associates and PA-API access.

Keep this one rule in mind first: your `.env` file contains secrets. Keep it private and never paste it into chat.

## What you need

- An Amazon Product Advertising API access key ID.
- An Amazon Product Advertising API secret access key.
- Your Amazon Associates partner tag.
- The right Amazon host, region, and marketplace for your store if you are not using Amazon US defaults.

## Step 1) Get your Amazon Associates and PA-API access

PA-API access usually comes from your Amazon Associates setup. The exact screen names can vary by region, so collect the access key, secret key, and partner tag from the Amazon side first.

## Step 2) Fill the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Fill in your access key ID, secret access key, and partner tag.
3. If you use a non-US Amazon store, also update the host, region, and marketplace values.

## Step 3) Run the first safe checks

These are the best first commands:

```bash
amazon-pa-api-tool --output json --version
amazon-pa-api-tool --output json auth check
amazon-pa-api-tool --output json product search --query "cast iron skillet" --limit 3
```

If the auth check passes and the sample search looks right, the setup is good enough to start real work.

## What to ask your agent next

- "Check the Amazon Product Advertising skill is connected, then search for 10 products in my niche."
- "Resolve these Amazon links into ASINs and build affiliate links for them."
- "Run this CSV research job and give me a summary of what worked."

## If something fails

The most common causes are:

- missing or invalid credentials
- the wrong host, region, or marketplace
- PA-API access not enabled for the account

Use [Troubleshooting](troubleshooting.md) if the auth check or first search fails.
