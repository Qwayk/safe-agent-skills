# Run your first Meta Ads report

From the downloaded tool folder, make a Python environment and install the CLI:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/meta-ads-api-tool onboarding
```

Add your token to the file onboarding shows. Confirm the connection and list the accounts you can read:

```bash
.venv/bin/meta-ads-api-tool --output json auth check
.venv/bin/meta-ads-api-tool --output json ad-accounts list --fields id,name
```

Replace `act_123456` and the dates with your account and period:

```bash
.venv/bin/meta-ads-api-tool --output json insights get --ad-account-id act_123456 --level campaign --fields campaign_id,campaign_name,impressions,clicks,spend --since 2026-01-01 --until 2026-01-07
```

Check the account and dates before using the numbers. Ask what changed in spend and results. A high click rate can tell you which ad caught people’s attention. If you care about sales or leads, check the matching outcome and the cost to get it.

## Look at an ad

Use the creative ID from the ad you want to review:

```bash
.venv/bin/meta-ads-api-tool --output json creatives anatomy --creative-id creative_123
.venv/bin/meta-ads-api-tool --output json previews get --creative-id creative_123 --ad-format DESKTOP_FEED_STANDARD
```

The first command shows the offer, copy, and creative links. The preview shows what Meta returned for the chosen placement. Preview HTML is untrusted content. See the [command guide](command_reference.md) for comparisons and the [export guide](snapshot_export.md) when you need to save the data.
