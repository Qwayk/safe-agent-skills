# OpenAI Ads

**Capability:** let an agent review, prepare, measure, and safely change ChatGPT Ads through the official OpenAI Ads API.

OpenAI Ads work can touch real budget, delivery, creative review, audiences, and conversion measurement. This skill gives your agent a safer way to answer practical ads questions before anything changes: what campaigns are live, which ad groups can serve, which ads are under review, what product-feed setup is missing, and whether conversion measurement is wired correctly.

You can ask for jobs like: “Show me all paused campaigns and the reason each one cannot serve,” “Prepare a paused campaign with San Francisco targeting,” “Check yesterday’s campaign performance by product,” or “Build a server-side conversion event plan but do not send it yet.”

The difference from a generic API helper is control. The agent can only use explicit OpenAI Ads commands. Reads run first. Writes create reviewed plans before live apply. Spend, serving, upload, audience, account, and measurement changes need extra approval. Secrets, pixel IDs, audience rows, customer IDs, raw emails, and conversion identifiers are redacted from normal output.

A useful first ask is: “Check my OpenAI Ads account connection, then list the commands you can use for campaigns, ad groups, ads, insights, audiences, files, conversions, targeting, and measurement.”

## Start here first

Run the onboarding command, add your Ads API key to `.env`, then check the account connection:

```bash
openai-ads-safe-agent-cli onboarding
openai-ads-safe-agent-cli auth check
```

No live ad change is made by either command.

## What this skill helps with

- Review account, campaign, ad group, ad, insight, custom audience, conversion, targeting, and file state.
- Prepare campaign, ad group, ad, brand, audience, upload, conversion, and status-change plans before apply.
- Build product-feed campaign setup using the public campaign, ad group, ad, and insights endpoints.
- Build image tags, review JavaScript Pixel setup guidance, list supported events, and plan server-side conversion sends.
- Keep local run summaries, plans, receipts, and audit logs for write-capable runs.

## Why this skill is different

Generic agents can improvise HTTP calls and accidentally change delivery, budget, targeting, audience data, or measurement. This skill keeps the agent inside named commands generated from the official OpenAI Ads OpenAPI spec and the official measurement docs.

Read commands can run directly. Write commands produce a plan. Live apply requires the saved plan, `--apply`, `--yes`, and extra acknowledgement when the change can affect spend, serving, uploads, audiences, account state, auth, or conversion measurement.

## What access this skill needs

For the Advertiser API, use an Ads Manager API key:

```bash
OPENAI_ADS_BASE_URL=https://api.ads.openai.com/v1
OPENAI_ADS_API_KEY=...
```

For server-side conversion events, also set:

```bash
OPENAI_ADS_PIXEL_ID=...
OPENAI_ADS_CONVERSIONS_API_KEY=...
OPENAI_ADS_CONVERSIONS_BASE_URL=https://bzr.openai.com/v1
```

Ads Manager Beta access, account verification, billing, and API-key issuance happen outside this CLI.

## Install and first run

Install slug: `openai-ads`

```bash
npx skills add Qwayk/safe-agent-skills@openai-ads -g -y
```

Then ask your agent to use the OpenAI Ads skill and run:

```bash
openai-ads-safe-agent-cli --output json api list
```

## How this skill stays safe

- Explicit commands only; no raw request bridge.
- Secrets and private measurement values are redacted.
- Reads run before writes whenever practical.
- Writes save a dry-run plan before live apply.
- Live apply requires a reviewed `--plan-in`.
- High-risk changes need `--ack-irreversible`.
- No-snapshot writes need `--ack-no-snapshot`.
- Receipts and local run summaries are saved for write-capable commands.

## What it covers today

The pinned official OpenAPI spec has 33 paths and 41 operations across campaigns, ad groups, ads, ad account, insights, custom audiences, conversions, targeting, and file upload. Manual coverage adds JavaScript Pixel guidance, image tag building, supported conversion events, server-side Conversions API sends, product-feed guidance, and campaign targeting guidance.

Full details are in [API coverage](docs/api_coverage.md).

## What happens before live changes

A write first returns a plan. The plan shows the operation, target IDs, redacted request body, risk reasons, before-state status, verification plan, and rollback limit. Apply refuses unless the same command is rerun with the reviewed plan and required approvals.

## Limits

Live Ads behavior is unverified until a real eligible Ads Manager Beta account, billing, verification, and API credentials are available. Product-feed connection and catalog upload happen in Ads Manager/SFTP, not through this API. The CLI does not promise rollback for Ads changes unless a specific command can truly provide it.

## Helpful docs

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Safety model](docs/safety_model.md)
- [API coverage](docs/api_coverage.md)
- [Proof](docs/proof.md)
- [Skill wrapper notes](docs/skills_wrappers.md)
