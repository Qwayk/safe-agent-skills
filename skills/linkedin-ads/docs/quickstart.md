# Check your account and run a report

Use this guide to get campaign spend, impressions, and clicks for one account. It also shows how to preview a proposed change without sending it to LinkedIn.

## Set up the tool

If you already have the `linkedin-ads-api-tool` command, start with [account setup](onboarding.md). To install it yourself, run these commands from the downloaded skill folder with Python 3.12 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
linkedin-ads-api-tool --output json --version
linkedin-ads-api-tool --output json onboarding
```

## Check the account

After adding your token, run:

```bash
linkedin-ads-api-tool --output json auth check
```

Choose an account ID from the result. You can also list the roles again with `ad-account-users list-authenticated-user`.

## Read campaign results

Replace `123456` and the dates below. This report shows impressions, clicks, and spend in the account's currency, grouped by campaign for the whole date range. LinkedIn includes both dates.

```bash
linkedin-ads-api-tool --output json ad-analytics analytics \
  --param 'accounts=List(urn:li:sponsoredAccount:123456)' \
  --param 'dateRange=(start:(year:2026,month:11,day:1),end:(year:2026,month:11,day:7))' \
  --param 'pivot=CAMPAIGN' \
  --param 'timeGranularity=ALL' \
  --param 'fields=pivotValues,impressions,clicks,costInLocalCurrency'
```

The token needs `r_ads_reporting`. An empty report can mean the account had no activity for those dates or the token lacks access to the requested data. Check both before treating the result as zero.

## Preview a campaign pause

Replace both example IDs with the account and campaign you mean. This command saves a plan in `plan.json` and sends no change to LinkedIn.

```bash
linkedin-ads-api-tool --output json --plan-out plan.json ad-campaigns update \
  --ad-account-id 123456 --campaign-id 789 \
  --body-json '{"patch":{"$set":{"status":"PAUSED"}}}'
```

Use the campaign ID from the report's `pivotValues` or from LinkedIn Campaign Manager. Review the account, campaign, and new status in the saved plan. The [approval guide](safety_model.md) explains when the tool can send the change and how to check the result.

Other useful first requests are “Show me the creatives running in this campaign” and “Check which lead forms or conversion events this account can see.” For all options, use the [command reference](command_reference.md).
