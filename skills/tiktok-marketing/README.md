# TikTok Marketing API

Find the right TikTok ad account, see which campaigns are running, and check what they spent and what they got back. You can also look at ad groups, creatives, pixels, and catalogs when your app has access.

Start with “Show me the TikTok ad accounts I can access, then pull last week's spend, impressions, and clicks for the account I choose.” Your agent checks the connection, shows the account names and IDs, and uses the account and dates you pick for the report.

For a change like pausing a campaign, the agent shows the account, campaign, and exact change first. If the tool cannot save the old settings, your approval also needs to cover going ahead without that copy.

## Start here first

- [Connect your TikTok ad account](docs/onboarding.md)
- [Run your first campaign report](docs/quickstart.md)
- [Review and check a change](docs/safety_model.md)

## What your agent can do

- Find ad accounts, campaigns, ad groups, and ads.
- Read spend, impressions, and clicks for the dates you choose. Check which pages of the report came back before adding up the rows.
- Inspect creatives, pixels, catalogs, and Business Center resources. Prepare a campaign change or upload for review.

## What happens before live changes

The agent saves a plan and waits for your approval. The tool checks that the saved plan still matches the request before sending it. A receipt records TikTok's reply. For a campaign pause, the agent can read the same campaign again to check its status.

## What access this tool needs

For the account check, you need a TikTok for Business app ID, app secret, and access token. TikTok also checks which ad accounts and features that token can use. Keep credentials on your computer.

## Install and first run

Ask your agent to install `tiktok-marketing` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@tiktok-marketing -g -y
```

Follow the [quickstart](docs/quickstart.md) to install the CLI, connect it, and read a report.

## What it covers today

The package includes 240 named API commands for the supported TikTok Marketing products. The [coverage table](docs/api_coverage.md) lists what the tool can call and where live access still needs checking.

## Helpful docs

- [Find a command](docs/command_reference.md)
- [Fix a connection or reporting problem](docs/troubleshooting.md)
- [See what has been checked](docs/proof.md)
