# Connect your Amazon Creators account

Amazon Creators needs local catalog credentials before an agent can check ASINs, classifications, variations, or parent items.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small catalog read and confirm the marketplace, locale, and partner tag are the ones you expected.

## Step 1: Create the local `.env` file

In the tool folder, copy `.env.example` to `.env`, then fill the Amazon Creators values you were given:

```dotenv
AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1
AMAZON_CREATORS_CREDENTIAL_ID=
AMAZON_CREATORS_CREDENTIAL_SECRET=
AMAZON_CREATORS_CREDENTIAL_VERSION=2.1
AMAZON_CREATORS_LOCALE=en_US
AMAZON_CREATORS_PARTNER_TAG=
```

Set `AMAZON_CREATORS_LOCALE` to the marketplace you want the agent to use. Keep the base URL as shown unless Amazon gives you a newer host.

## Step 2: Use a saved token when you have one

If `.state/token.json` already exists, keep it local and let the tool use it. Token fetch and token set helpers can write local token state, so review the plan before allowing them to run.

## Step 3: Check the connection

Run:

```bash
amazon-creators-api-tool auth check
```

Then ask the agent to list supported locales or run one small item lookup before deeper catalog work.

## What to ask your AI agent (examples)

- Show me the plan that spells out the locale, marketplace, and resources you intend to request before any live catalog call.
- Gather the classifications, technical info, and variation summary for an ASIN, and wait for my approval before fetching real data.
- List the supported locales first so the marketplace header aligns with the region I care about before we move forward.
- Treat the dry-run plan as your audit log and only release the actual browse-node hierarchy once I explicitly give the go-ahead.
