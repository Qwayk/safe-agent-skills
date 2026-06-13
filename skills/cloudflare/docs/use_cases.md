# What you can do with Cloudflare

Cloudflare work usually starts when something important depends on the edge: DNS must point to the right place, a Worker route may affect production traffic, a security rule needs review, or a Zero Trust policy may decide who can reach an internal app.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent inspect the account, explain what it found, and prepare careful plans before anything changes DNS, Workers, Pages, Zero Trust, account access, logs, or sensitive files.

## Good jobs to give the agent

### Account, zone, and DNS review

- "List my Cloudflare accounts and zones, then tell me which zone looks like the one for this website."
- "Show all DNS records for this zone and flag anything that looks stale, duplicated, proxied unexpectedly, or pointed at an old host."
- "Check DNSSEC and important zone settings before we change anything."
- "Export the zone DNS records to a local file so we have a review copy."
- "Run zone-create-check before we plan onboarding a new domain."

### Workers, Pages, and edge routing

- "List Workers scripts, routes, deployments, schedules, and usage settings for this account."
- "Check whether this route points to the Worker we expect."
- "Review Pages projects and deployments before we update a production branch or domain."
- "Download one Worker script to a local file for review without printing the code in chat."
- "Prepare a plan for a Worker route change and explain the risk before any apply step."

### Zero Trust, access, and security posture

- "List Access apps and policies so I can see who can reach this internal tool."
- "Review Gateway rules, lists, logging settings, and DLP profiles."
- "Show account members, roles, API tokens, and organizations in a file-safe way."
- "Find Cloudflare audit events or Error ID logs and save the details locally."
- "Tell me what extra token scope or role is missing if a security surface cannot be read."

### Careful change planning

- "Prepare a DNS record update plan, but do not change the zone until I approve the exact target."
- "Plan a Logpush, Pages, Worker route, or Zero Trust policy update and show the approval needed."
- "Use the broader allowlisted operations surface only when a named command is not the right fit."
- "For anything destructive or secret-bearing, save results to a local file and explain what cannot be undone automatically."

## What the agent should show you

- The account, zone, Worker, route, Pages project, policy, token, log source, or DNS record it checked.
- A short explanation of what matters, not only raw JSON.
- A local file path when the result may contain secrets, private code, logs, member details, or other sensitive data.
- A dry-run plan before DNS, Workers, Pages, Zero Trust, member, token, or operations changes.
- Any missing Cloudflare permission, account role, token scope, or product enablement that blocks the work.
- A receipt, clear refusal, or read-back result after an approved action.

## Good first Cloudflare path

Start by checking auth, listing accounts and zones, choosing one zone, exporting DNS records, and running `auth zone-create-check` before planning any onboarding or live DNS work.
