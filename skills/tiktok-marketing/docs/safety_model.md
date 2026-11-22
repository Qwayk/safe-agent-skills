# Review and check a TikTok campaign change

Run `auth check` to see which ad accounts you can use. It contacts TikTok directly. For other reads, `--live` sends the request to TikTok. The same command without `--live` shows what it would send.

## Review the saved plan

Run the change command with `--plan-out plan.json` and without `--apply`. Check the ad account, the campaign or other item, and the exact change. The tool records when it cannot save the old settings. You need to explicitly approve going ahead without that saved copy. The tool has no automatic restore for those operations.

For the campaign pause in the [quickstart](quickstart.md#preview-a-campaign-pause), the approved command is:

```bash
tiktok-marketing-api-tool --output json --live --apply --yes \
  --plan-in plan.json --ack-irreversible --ack-no-snapshot \
  --receipt-out receipt.json api campaign-status-update
```

The tool uses the saved inputs. If the account, campaign, change, or credentials differ, save a new plan and review it again. If the output says `refused: true`, read the reason before taking any further action.

## Check what happened

The receipt shows TikTok's response. To check whether the pause took effect, read the same campaign and check its `operation_status`. Replace the example account and campaign IDs below with the IDs in the saved plan.

```bash
tiktok-marketing-api-tool --output json --live api campaign-get \
  --query advertiser_id=123456 --query 'filtering={"campaign_ids":["321"]}'
```

If a write times out or the reply is unclear, read the item first so you can decide whether the change still needs to be sent. Use `runs list` and `runs show` to find local records of plans, refusals, and receipts. Keep credentials and private account details out of shared logs.
