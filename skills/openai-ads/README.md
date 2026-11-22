# OpenAI Ads

Use this tool to check how your ChatGPT ads are doing. Ask your agent to show what spent money, find paused ads, or check which conversion events a campaign measures.

Start with your Ads account and a short campaign list. If you want a change, ask the agent to show the exact plan first. You decide whether it can change the account.

## Install and try it

```bash
npx skills add Qwayk/safe-agent-skills@openai-ads -g -y
```

> Check my Ads account, show up to ten campaigns, and tell me which ones are paused.

Use the [Quickstart](docs/quickstart.md) to install the CLI and make your first read. The [setup guide](docs/onboarding.md) explains which Ads Manager key to use and where to keep it.

The tool can read campaign results and prepare changes to campaigns, ads, audiences, and conversion settings. The command list includes 40 Advertiser API operations plus local guidance for targeting, product feeds, and measurement. [API coverage](docs/api_coverage.md) shows the exact commands.

- [Approval and receipts](docs/safety_model.md)
- [Command guide](docs/command_reference.md)
- [All OpenAI Ads docs](docs/README.md)
