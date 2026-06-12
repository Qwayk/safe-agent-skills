# What you can do with Instantly

Instantly work usually starts with campaign and deliverability questions: which campaigns are healthy, which sending accounts are risky, which leads need cleanup, and which changes should wait for review.
If you need setup first, start with [Connect your Instantly account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good jobs to give the agent

### Campaign and deliverability review

- "Show me which active campaigns look weak or risky right now."
- "Pull campaign analytics for the last 7 days and highlight what changed."
- "Check account warmup and vitals so I can see which sending accounts need attention."
- "Review inbox placement results and summarize the biggest deliverability problems."

### Lead and list operations

- "Audit my lead lists, labels, and custom tags before we clean anything up."
- "Preview moving or bulk assigning these leads, but stop before apply."
- "Prepare a lead patch from this file and show me the plan first."
- "Check whether this lead or campaign target is valid before changing anything."

### Webhooks, workspace, and admin work

- "Review my webhooks and tell me which ones look stale or risky."
- "Show me my workspace health and who has access before we change settings."
- "Prepare a careful workspace or campaign change and keep a receipt of what changed."
- "Check API-key or account-management flows safely without exposing secrets in chat."

## What you should expect from the agent

For review work, the agent should show the campaign, account, lead, or webhook IDs it checked and explain the few signals that matter most.

When you ask for a change, the agent should:

1. Check auth and discover the right target first.
2. Show a dry-run plan of what would change.
3. Apply only after explicit approval and any required extra acknowledgements.
4. Verify after apply and point you to the saved proof files.
