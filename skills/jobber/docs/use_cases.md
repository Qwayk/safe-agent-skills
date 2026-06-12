# What this skill can help you do

Jobber work usually starts with service-business questions: which clients, jobs, invoices, quotes, visits, or webhook events need attention, and what would a safe change plan look like before anything updates live data?

## Good first asks

- "Check what this skill can review safely and show me the top 5 actionable findings."
- "Run a small read across clients and tell me what changed recently."
- "Prepare a safe plan for one update, and wait for my approval."
- "Create a short webhook topic list to check if our app is subscribed correctly."

## Good jobs to give the agent

- Checking Jobber account visibility before any change.
- Pulling structured read data for review (`clients`, `jobs`, `invoices`, etc.).
- Planning write operations from exact mutation families.
- Validating webhook signature behavior for incoming payload checks.
- Preparing batch CSV runs for repeatable safety workflows.

## What the agent should show you

When setup is correct, the agent should return:

- A clear first check result from `auth check`.
- Read output in JSON that is easy to read.
- A write plan before any live write.
- Explicit approval requirements for any write execution.
- A traceable proof artifact path for review.
