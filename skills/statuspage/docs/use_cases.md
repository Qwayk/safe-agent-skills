# What you can do with Statuspage

Statuspage work usually starts with a simple operational question: is the vendor healthy enough for us to deploy, launch, debug, or answer a customer?
If you need setup first, start with [Use a public Statuspage URL](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

No account is needed for public pages. The main thing to check is that the agent is looking at the right vendor page, because public status pages do not always show every private customer issue.

## Good jobs to give the agent

### Before deploys, launches, or migrations

- "Check this vendor's status page before we start the deploy."
- "Tell me whether any component we depend on is degraded right now."
- "Check open incidents and scheduled maintenance before we send this launch email."
- "Compare the status pages for our payment, email, hosting, and analytics vendors before today's rollout."

### Support and customer replies

- "Summarize the current incident in plain English so support can reply to customers."
- "List the latest updates for this open incident and tell me whether the vendor says it is resolved."
- "Check whether this looks like our outage or the vendor's outage."
- "Create a short internal note: current status, affected components, incident link, and next check time."

### Daily operations and handoffs

- "Create a daily read-only status snapshot for handoff."
- "List scheduled maintenance windows for this vendor this week."
- "Check whether any listed component changed from operational to degraded."
- "Run the same status check on these public pages and show me the ones that need attention."

## What the agent should show you

- The public page URL it checked.
- The overall status and the exact incident or maintenance titles that matter.
- Any affected components, time windows, and latest update text.
- A short plain-English summary before the raw data.
- A clear note when the page exposes limited component or incident detail.

## Good first check

Ask the agent to check one public Statuspage URL, summarize open incidents and scheduled maintenance, and tell you whether anything should delay the work you were about to do.
