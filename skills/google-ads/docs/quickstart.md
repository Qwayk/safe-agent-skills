# Quickstart

Start with a small Google Ads read: checking accounts, presets, and campaign data before you touch spend.

Need more ideas? See [What you can do with Google Ads](use_cases.md). Need setup help? See [Connect your Google Ads account](onboarding.md).

A good first ask is:

> Show which Google Ads accounts I can access and confirm the customer IDs.

## What you will do first

1. Make sure the local tool can run.
2. Check the account or connection before asking for real work.
3. Run one small read and make sure the result matches the real service.
4. Ask for a reviewed plan before any change that could affect live data, spend, content, customers, or settings.

## 1. Install or open the tool

If `google-ads-api-tool` already runs, go to step 2. Otherwise, open the Google Ads tool folder and use Python 3.11 or newer. Run the following commands, then keep using the same terminal for the rest of this guide.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
google-ads-api-tool onboarding
```

```bash
google-ads-api-tool auth check
```

## 3. Run one small first read

Start by confirming the customer IDs available to your OAuth user:

```bash
google-ads-api-tool customers list-accessible
```

Then preview the report pack:

```bash
google-ads-api-tool presets list
google-ads-api-tool presets show --preset optimization_pack_v1
google-ads-api-tool presets show --preset analysis_pack_v2
google-ads-api-tool presets show --preset analysis_pack_max_v1
google-ads-api-tool presets validate
```

```bash
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack
```

The export command above previews the plan. Add `--apply --yes` to fetch account data and write the local pack; this does not change Google Ads. Then ask the agent to summarize the report and name anything missing, empty, or blocked.

## 4. Before changing the account

Run a preview and save it with `--plan-out PATH.json`. For a budget change, read the budget and currency in the confirmed account. Show the user the customer ID, the campaign or shared budget, and the current and proposed amounts in that currency. Ask them to approve that exact change and its effect on spending.

The [safety guide](safety_model.md) explains when the tool needs the matching saved plan and extra approval, and how to check what Google changed. See the [command reference](command_reference.md) for the exact options.

## What a useful first result includes

A good first result should make these things clear:

- what was checked
- whether the connection worked
- what came back from the service
- what the result means in plain English
- what is safe to inspect next
- where any saved file, export, plan, or receipt was written

## Where to go next

- For real examples, read [What you can do](use_cases.md).
- For setup details, read [Connect your Google Ads account](onboarding.md).
- For Google Ads workflow examples, read [Media buyer quickstart](media_buyer_quickstart.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
