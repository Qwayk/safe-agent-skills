# What you can do with Jobber

Jobber is useful when a service business needs a clear view of clients, jobs, quotes, invoices, visits, or webhook events before someone changes the schedule or customer record.

This skill lets an agent inspect the Jobber account, pull structured business data, prepare reviewed change plans, and help with webhook checks. The best first use is usually not "change this record." It is "show me what is true right now, then help me decide the safest next action."

If you need setup first, start with [Connect your Jobber account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good first asks

- "Check whether this Jobber connection works, then show what account areas the agent can review."
- "Pull the latest clients, jobs, invoices, and quotes I should look at today."
- "Find recently updated jobs and tell me which ones may need follow-up."
- "Show upcoming visits and flag anything that looks missing, duplicated, or unclear."
- "List the webhook topics this app can use and explain which ones matter for job updates."

## Everyday service-business jobs

Use Jobber when the agent needs to help with real operating questions:

- "Which customers have open jobs but no recent activity?"
- "Which quotes are still waiting and should be followed up?"
- "Which invoices look unpaid or need a customer-friendly reminder?"
- "What changed in the schedule since yesterday?"
- "Which jobs are connected to this client, and what is the next step?"
- "Can you prepare a small update plan for these records and stop before anything changes?"

These are the jobs where an agent can save time without pretending it understands the business better than the person running it.

## Change planning

When you ask for a Jobber change, the agent should treat it like live customer data:

1. Read the target record first when possible.
2. Show the exact change plan.
3. Explain which mutation family would be used.
4. Wait for approval before applying anything.
5. Save a receipt or clear refusal so you can review what happened later.

This matters because a small field update can affect a real customer, invoice, quote, visit, or operations workflow.

## Webhook checks

Jobber webhooks are useful when you want another system to react to business events. Good asks include:

- "Show the webhook topics available for this account."
- "Help me check whether this incoming webhook signature is valid."
- "Explain which webhook topics would matter if we want alerts for new jobs or invoice changes."

The agent should not guess from a payload alone. It should name what it checked and what still needs a real Jobber app or account permission.

## What the agent should show you

A useful Jobber answer should include:

- the account or connection check result
- the exact objects reviewed, such as clients, jobs, invoices, quotes, visits, or webhook topics
- a short plain-English summary of what matters
- the safest next action
- the approval needed before a live write
- any saved plan, receipt, or local output file that helps you audit the work

## Honest limits

Jobber access depends on the connected app, account permissions, and the records exposed to that app. If the agent cannot see a record or mutation safely, it should say that plainly and stop instead of inventing a workaround.
