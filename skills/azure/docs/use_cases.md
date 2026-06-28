# Use cases

Use this tool when you want Azure work that is reviewable before execution.

## Good first asks

- "Show me what this subscription has in this resource group, then summarize risk points."
- "List which operations are safe read actions I can run first for this task."
- "Create a write plan from this CSV and stop for approval before apply."

## Common user workflows

- Audit subscriptions, resource groups, and resource state before any change.
- Inspect data-plane objects where a management endpoint read is not enough.
- Build batch plan files for repeatable operations and review before running.
- Capture local proof for every run through plan and receipt output.

## What you should get back

The agent should return a short summary, the Azure area it checked, any risk it found, and whether it stopped before a live change.

## Where this works best

- When you need explicit planning before writes.
- When your operator wants a plan and a separate approval before any live write.
- When run history and artifact evidence are required.

## Where to set expectations

- This is Azure REST API operations, not Microsoft Graph or non-Azure Microsoft products.
- Live change verification is still a manual or future-cloud integration task.
