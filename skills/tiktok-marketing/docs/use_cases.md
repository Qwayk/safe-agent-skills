# What you can do with TikTok Marketing

TikTok Marketing work usually starts with one access check and one advertiser question: does the token work, which advertiser can we reach, what campaigns or ads exist, and which pinned operation fits the report, upload, or campaign change the team wants.
If you need setup first, start with [Connect your TikTok Marketing account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent confirm access, review advertiser and campaign data, plan reports or asset uploads, and prepare campaign-change plans before anything writes to TikTok.

## Good jobs to give the agent

### Auth and advertiser access

- "Check whether my TikTok Marketing app credentials and access token work."
- "Tell me which advertiser read is the safest first proof that setup is working."
- "Show whether this advertiser, campaign, ad group, ad, creative, pixel, catalog, or business-center request has the right context."
- "Explain which request file, query file, advertiser permission, or token issue blocks the next step."

### Campaign, ad, and creative review

- "Pull a simple campaign summary for this week."
- "Show the current ad group and ad state before we plan changes."
- "Review advertiser or campaign data first so we do not guess the target."
- "Check creatives, pixels, catalogs, and business-center data before an upload or campaign update."

### Reports, uploads, and pinned operations

- "Plan a report task and show the request before anything runs live."
- "Prepare the safe first plan for an image or video upload flow."
- "Show the exact pinned operation for this TikTok job before we try it."
- "Tell me when a read needs `--live` and when a write-like operation must stay as a plan first."

### Careful change planning

- "Show exactly what TikTok API call would run before any live write."
- "Prepare a reviewed campaign, ad group, ad, creative, report, or upload plan."
- "Explain the write gates and no-snapshot limit before provider HTTP."
- "Save the plan or refusal so another person can review it later."

## What the agent should show you

- The credential status, advertiser, campaign, ad group, ad, creative, pixel, catalog, business-center object, report, upload, or pinned operation it checked.
- The query or body file needed for the operation.
- A dry-run plan before campaign, ad, creative, upload, or other write-like work.
- Any `--live`, apply, no-snapshot, advertiser-permission, token, request-shape, or pinned-operation gate.
- The saved plan, refusal, run history, or live-read result after the request.

## Good first TikTok Marketing path

Start with `auth check`, choose one advertiser context, run one small campaign or advertiser read, then ask the agent to identify the pinned operation before planning any upload or campaign change.
