# OpenAI Ads

The ChatGPT Ads API tool for agents helps you manage your ChatGPT ads.

You can ask your agent to check results, find problems, create new campaigns, update ads, review audiences, and check whether conversion tracking is working.

For example: "Check the stats for this campaign," "Find ads that are not running," "Create a new paused campaign for this service," or "Tell me if tracking is missing anything important."

The agent starts by reading your account and explaining what it found. If you ask it to change something live, like a campaign, ad, audience, or tracking setup, it shows you the change first and waits for your approval.

A good first ask is: "Check my OpenAI Ads account connection, then show me what campaign, ad, audience, tracking, and reporting work you can help with."

## Start here first

If you are setting this up for the first time, run onboarding, add your Ads API key to `.env`, and check the account:

```bash
openai-ads-safe-agent-cli onboarding
openai-ads-safe-agent-cli auth check
```

Those commands do not change ads. The account check reads the ad account so you know the connection works before asking for reports or changes.

## What your agent can do

Your agent can help with everyday ChatGPT Ads work:

- Check account, campaign, ad group, ad, audience, file, targeting, and conversion setup.
- Find campaigns or ads that are paused, blocked, missing setup, or not ready to serve.
- Read campaign, ad group, ad, and account insights where the Ads API provides them.
- Prepare new campaigns, ad groups, ads, audiences, uploads, conversion settings, and status changes.
- Build image tags, list supported conversion events, and prepare server-side conversion event sends.
- Explain product-feed campaign setup, while leaving feed connection and catalog upload to Ads Manager or SFTP.

For exact commands, use the [command guide](docs/command_reference.md).

## What happens before live changes

Reads can run directly. That means your agent can check the account, list campaigns, inspect targeting options, or pull insights without changing anything.

Changes work differently. If you ask the agent to create, update, pause, activate, upload, or send measurement data, the tool first writes a plan. The plan shows the target, the requested change, the private values hidden from normal output, the risks, and what can and cannot be checked before the change.

The agent should show you that plan before anything live happens. Real changes need your approval, the saved plan, and extra acknowledgement when the change can affect spend, serving, audiences, uploads, account state, auth, or measurement. When the tool cannot save a useful before-state, it says that clearly before it lets the change continue.

The tool does not promise rollback for Ads changes unless a specific command can truly provide it.

## What access this tool needs

For normal Ads work, you need an Ads Manager API key:

```bash
OPENAI_ADS_BASE_URL=https://api.ads.openai.com/v1
OPENAI_ADS_API_KEY=...
```

For server-side conversion events, you also need the Pixel ID and Conversions API key:

```bash
OPENAI_ADS_PIXEL_ID=...
OPENAI_ADS_CONVERSIONS_API_KEY=...
OPENAI_ADS_CONVERSIONS_BASE_URL=https://bzr.openai.com/v1
```

Ads Manager Beta access, account verification, billing, and API-key issuance happen outside this tool.

## Install and first run

Install slug: `openai-ads`

```bash
npx skills add Qwayk/safe-agent-skills@openai-ads -g -y
```

Then ask your agent:

```text
Use the OpenAI Ads tool. Check the account connection, list the available Ads tasks, and suggest one safe read before planning any changes.
```

You can also run:

```bash
openai-ads-safe-agent-cli --output json api list
```

## What it covers today

The tool follows the official OpenAI Ads API spec currently pinned in this repo: 33 paths and 41 operations for campaigns, ad groups, ads, ad account, insights, custom audiences, conversions, targeting, and file upload.

It also includes helper commands for official measurement and setup docs: JavaScript Pixel guidance, image tag building, supported conversion events, server-side Conversions API sends, product-feed guidance, and campaign targeting guidance.

Full details are in [API coverage](docs/api_coverage.md).

## Limits

Live Ads behavior has not been tested against a real eligible Ads Manager Beta account yet. That still needs real Ads Manager Beta access, billing, account verification, and API credentials.

Product-feed connection and merchant catalog upload are not handled by this API tool. Those steps happen in Ads Manager or over SFTP.

This tool is only for ChatGPT Ads / OpenAI Ads. Use the separate OpenAI Platform tool for normal OpenAI API work such as models, files, assistants, vector stores, batches, or fine-tuning.

## Helpful docs

- [Get one safe first result](docs/quickstart.md)
- [Browse the docs by task](docs/README.md)
- [See real agent asks](docs/use_cases.md)
- [Understand approvals before changes](docs/safety_model.md)
- [Look up exact commands](docs/command_reference.md)
- [Check API coverage](docs/api_coverage.md)
- [See what was tested](docs/proof.md)
- [Read the skill wrapper notes](docs/skills_wrappers.md)
