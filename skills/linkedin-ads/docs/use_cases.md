# What you can do with LinkedIn Ads

LinkedIn Ads work usually starts with access and approval: which ad accounts the token can see, whether the app has the right LinkedIn product approval, which campaigns or creatives need review, and whether lead forms, conversions, targeting, or tracking are available.
If you need setup first, start with [Connect your LinkedIn Ads account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent check access, review B2B campaign data, surface LinkedIn approval gates, and prepare campaign or creative changes before anything writes to the ad account.

## Good jobs to give the agent

### Access and account checks

- "Check my LinkedIn Ads token, list the ad accounts I can access, and flag approval problems."
- "Tell me which account, organization, campaign group, campaign, or creative this request targets."
- "Show whether restricted families are access-gated, private-api-gated, tier-gated, or live-unverified."
- "Explain which product approval, scope, account permission, or resource ID is missing."

### Campaign, creative, and analytics review

- "Show campaign groups, campaigns, creatives, and one analytics pull for this ad account."
- "Review sponsored creatives and previews before I change anything."
- "Pull campaign performance and explain what looks worth human review."
- "Check whether lead forms, lead responses, conversions, tracking tags, or insight tags are available."

### Audience and approval-gated work

- "Check whether Matched Audiences, Audience Insights, Media Planning, or Company Intelligence is available for this app."
- "Review targeting or audience-related commands before we build a plan."
- "Tell me when a LinkedIn approval gate is the real blocker instead of a tool problem."
- "Prepare a handoff that separates working account reads from restricted API areas."

### Careful change planning

- "Prepare a campaign update plan so I can review the exact account and payload before anything changes."
- "Preview a creative, lead, conversion, tracking, or permission-changing action."
- "Explain when delete, batch-write, or permission-changing work needs stronger approval."
- "Show the no-snapshot limit before any live LinkedIn write."

## What the agent should show you

- The token status, ad account, organization, campaign group, campaign, creative, lead, conversion, audience, or tracking target.
- The approval or access label when LinkedIn blocks a family.
- A dry-run plan before create, update, delete, batch, creative, conversion, lead, or permission-changing actions.
- Any `--apply`, `--yes`, irreversible, no-snapshot, saved-plan, product-approval, or scope gate.
- The saved plan, run artifact, refusal, or live-read result after the request.

## Good first LinkedIn Ads path

Start by checking the token, listing visible ad accounts, pulling one campaign or analytics read, and asking the agent to name any LinkedIn approval gates before planning a write.
