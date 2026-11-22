# Choose an ad account and run a report

Use this guide to get spend, impressions, and clicks by campaign for one TikTok ad account. It also shows how to save a campaign pause for review.

## Set up the tool

If the `tiktok-marketing-api-tool` command is already available, go straight to [account setup](onboarding.md). To install the CLI yourself, run this from the downloaded skill folder with Python 3.12 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
tiktok-marketing-api-tool --output json --version
tiktok-marketing-api-tool --output json onboarding
```

After [adding your credentials](onboarding.md#add-your-app-and-token), run:

```bash
tiktok-marketing-api-tool --output json auth check
```

Choose the ad account by its name and ID. TikTok calls that ID `advertiser_id`.

## Run a seven-day report

Replace `123456` and the dates with the account and week you want. The command reads TikTok when you include `--live`. Without it, the tool shows the request it would send.

```bash
tiktok-marketing-api-tool --output json --live api report-integrated-get \
  --query-json '{"advertiser_id":"123456","report_type":"BASIC","data_level":"AUCTION_CAMPAIGN","dimensions":["campaign_id"],"metrics":["spend","impressions","clicks"],"start_date":"2026-11-01","end_date":"2026-11-07","page":1}'
```

Look for rows in `receipt.response.body.body.data.list` and check `page_info` in the same `data` object. If `total_page` is greater than one, rerun the same request with the next `page` number until you reach the last page. Keep the same account, dates, and metrics for each page. Tell the reader if any page is missing before reporting a total.

## Preview a campaign pause

Replace the example ad account and campaign IDs. This saves `plan.json` for review and makes no request to change the account.

```bash
tiktok-marketing-api-tool --output json --plan-out plan.json api campaign-status-update \
  --body-json '{"advertiser_id":"123456","campaign_ids":["321"],"operation_status":"DISABLE"}'
```

Check the account, campaign, and requested status in the plan. See [how to approve and check the result](safety_model.md) before sending the change.
