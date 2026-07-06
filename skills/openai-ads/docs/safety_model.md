# Safety Model

ChatGPT Ads changes can affect money, delivery, audiences, creative review, account state, and conversion reporting. The tool is built so the agent looks first and changes later.

## What the agent can do by itself

The agent can run reads. It can check the account, list campaigns, inspect ads and ad groups, look up targeting, pull insights, list supported conversion events, and explain product-feed or tracking setup.

Those reads still hide secrets and private customer or measurement values from normal output.

## What waits for your approval

Anything that changes the account starts as a plan. This includes creating or updating campaigns, ads, ad groups, custom audiences, conversion settings, uploads, status changes, and server-side conversion event sends.

The plan shows:

- what the agent wants to do
- which account object or measurement event is involved
- the private values hidden from normal output
- why the change is risky
- whether the tool could check current state first
- what the tool can check after the change
- whether rollback is supported

The agent should show you the plan before continuing.

## Changes that need extra care

Some changes need stronger approval because they can affect spend, delivery, data, or reporting:

- activating, pausing, or archiving ad accounts, campaigns, ad groups, or ads
- budget, bid, targeting, and serving changes
- custom audience creation, upload, and archive
- file upload
- conversion API keys, event settings, pixels, and server-side conversion events
- account brand and account serving-state changes

The tool checks both the command and the request body. For example, if a campaign body includes a budget, active status, or targeting, the change is treated as high risk even if the command name sounds simple.

## Server-side conversion events

Conversion events can affect reporting and optimization, so the tool prepares them first. A real send needs your approval, the saved plan, and acknowledgement that the event cannot be unsent by this tool.

Event source URLs, identifiers, customer fields, and conversion API keys are hidden from normal output.

## No rollback promise

The tool does not promise rollback for Ads changes. When it cannot save a useful before-state, the plan says so and the agent must ask for no-snapshot approval before continuing.

That means your safest workflow is:

1. Ask the agent to read first.
2. Review what it found.
3. Ask for a plan.
4. Approve only after the target, risk, and limit are clear.
