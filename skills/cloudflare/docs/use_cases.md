# What you can do with Cloudflare

Ask your agent to trace where a domain points, check a Worker route or find who can reach an internal app. If you are new to the tool, see [how to connect your account](onboarding.md) and [run your first read](quickstart.md). The [command guide](command_reference.md) has the exact options.

## Good jobs to give the agent

### Account, zone, and DNS review

- "List my Cloudflare accounts and zones, then tell me which zone looks like the one for this website."
- "Show all DNS records for this zone and flag anything that looks stale, duplicated, proxied unexpectedly or pointed at an old host."
- "Check DNSSEC and important zone settings before we change anything."
- "Export the zone DNS records to a local file so we have a review copy."
- "Run zone-create-check before we plan onboarding a new domain."

### Workers, Pages, and edge routing

- "List Workers scripts, routes, deployments, schedules, and usage settings for this account."
- "Check whether this route points to the Worker we expect."
- "Review Pages projects and deployments before we update a production branch or domain."
- "Download one Worker script to a local file for review without printing the code in chat."
- "Prepare a plan for a Worker route change and explain the risk before any apply step."

### Zero Trust and account access

- "List Access apps and policies so I can see who can reach this internal tool."
- "Review Gateway rules, lists, logging settings, and DLP profiles."
- "Show account members, roles, API tokens, and organizations and save private results to a local file."
- "Find Cloudflare audit events or Error ID logs and save the details locally."
- "Tell me what extra token scope or role is missing if a security surface cannot be read."

### Careful change planning

- "Prepare a DNS record update plan, but do not change the zone until I approve the exact target."
- "Plan a Logpush, Pages, Worker route, or Zero Trust policy update and show the approval needed."
- "If there’s no named command for this job, show me which supported operation fits."
- "For anything destructive or secret-bearing, save results to a local file and explain what cannot be undone automatically."

## What the agent should show you

- The account, zone, Worker, route, Pages project, policy, token, log source, or DNS record it checked.
- A short explanation of what matters, not only raw JSON.
- A local file path when the result may contain secrets, private code, logs, member details, or other sensitive data.
- A dry-run plan before DNS, Workers, Pages, Zero Trust, member, token, or operations changes.
- Any missing Cloudflare permission, account role, token scope, or product enablement that blocks the work.
- A receipt, clear refusal, or read-back result after an approved action.

## Good first Cloudflare path

Start by checking auth, listing accounts and zones, choosing one zone, exporting DNS records, and running `auth zone-create-check` when planning to onboard domains in bulk.
