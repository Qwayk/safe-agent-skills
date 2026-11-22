# LinkedIn Ads

Find the right LinkedIn ad account, see which campaigns are running, and check what they spent and what they got back. You can also look at ad previews, lead forms, and conversion tracking when your account has access.

Start with a request like “Show me which ad accounts I can access. Then pull last week's spend, impressions, and clicks for the account I choose.” Your agent checks your connection and shows which account and dates the report uses.

For a change like pausing a campaign, the agent first shows the account, campaign, and exact change. You decide whether it goes ahead. LinkedIn changes made through this tool have no saved copy of the previous settings.

## Start here first

- [Connect your LinkedIn Ads account](docs/onboarding.md)
- [Run your first report](docs/quickstart.md)
- [See what you approve before a change](docs/safety_model.md)

## What your agent can do

- Find ad accounts, campaign groups, campaigns, and creatives. Open a preview when you want to see the ad before changing it.
- Read clicks, impressions, and spend for a set of dates. Check available lead forms, conversions, and tracking tags.
- Prepare changes to campaigns, audiences, creatives, and account roles. Access depends on your LinkedIn app, token permissions, and account role.

## What happens before live changes

The agent prepares a plan and waits for your approval. It also needs your explicit approval to send the change without a saved copy of the old settings. Deletes, batch changes, and changes to who has access need extra confirmation and the matching saved plan. A receipt shows LinkedIn's reply. The agent can then use a separate read to check the result when the API allows it.

## What access this tool needs

Use an access token from your approved LinkedIn app. Your LinkedIn member account needs the right role for the ad account. Reports also need the `r_ads_reporting` permission. LinkedIn gives some products, such as Audience Insights and Matched Audiences, separate approval.

## Install and first run

Ask your agent to install `linkedin-ads` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@linkedin-ads -g -y
```

Once installed, ask your agent to set up the CLI and check which ad accounts you can access. Keep the token on your computer. The [first report guide](docs/quickstart.md) shows how to install the CLI and run the commands yourself.

## What it covers today

The tool covers ad accounts, campaign groups, campaigns, creatives, reports, lead forms, conversions, targeting, audiences, previews, and tracking. The [API coverage table](docs/api_coverage.md) lists the commands, the access each needs, and where live checks are still pending.

## Helpful docs

- [Browse all LinkedIn Ads docs](docs/README.md)
- [Find a command](docs/command_reference.md)
- [Fix a setup or reporting problem](docs/troubleshooting.md)
- [See what has been checked](docs/proof.md)
