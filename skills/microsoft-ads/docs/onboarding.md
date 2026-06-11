# Onboarding

Use this page when you want the shortest safe setup path for Microsoft Ads.

This tool runs locally and needs a Microsoft Advertising developer token plus a local OAuth token JSON for live reads or writes.
Keep your `.env` file and token file private, and never paste them into chat.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill the fields you need:

```text
MSADS_ENVIRONMENT=prod
MSADS_DEVELOPER_TOKEN=
MSADS_CUSTOMER_ID=
MSADS_CUSTOMER_ACCOUNT_ID=
MSADS_TIMEOUT_S=30
```

If you want the tool to create the starter file for you, run:

```bash
msads-api-tool onboarding
```

## Step 2: Store your OAuth token JSON locally

After you complete your Microsoft Ads OAuth flow and save the token JSON file, store it locally with:

```bash
msads-api-tool auth token set --file token.json
```

The tool keeps that token under `.state/token.json` next to your `.env` file.

## Step 3: Check setup before real work

Ask your agent to start with safe checks like:

- "Check the Microsoft Ads skill is configured."
- "Show me which live reads are safe to run first."
- "Find the safest reporting or account review path for this job."

If you want to run the first checks yourself:

```bash
msads-api-tool --output json --version
msads-api-tool auth token status
msads-api-tool --output json --live auth check
```

The first two checks stay local. The last one is your first real Microsoft Ads network read.

## Step 4: First requests to give your agent

These are good first requests in plain English:

- "Review my accounts or campaigns safely first."
- "Pull a performance report for the last 30 days and save it for me."
- "Prepare the write plan first and show me the approval steps."
- "For any budget, delete-like, or batch action, save the plan and make me review it before apply."

## Step 5: If something fails

The most common setup problems are:

- the developer token is missing or wrong
- the OAuth token JSON is missing, expired, or for the wrong account
- the customer ID or account ID is wrong for this task
- the Microsoft Ads account or network path blocks the request

Use [Troubleshooting](troubleshooting.md) if the first checks fail.
