# Useful Google Cloud asks

If you are not sure where to start, ask for a read-only review of what the current Google Cloud identity can see. A good first answer should name the project or quota context, show one useful area, and stop before changing anything.

Google Cloud can affect production apps, public access, data, permissions, and spend. The safest useful pattern is simple: look at the target first, explain what matters, then prepare a plan only if a change is needed.

## Good first asks

- "Check which Google Cloud projects this account can see and tell me which one looks like the right target."
- "Show enabled services in this project and flag anything that looks cost-sensitive or worth reviewing."
- "Review IAM access and tell me which users, groups, roles, or service accounts deserve a human check."
- "List Compute Engine instances in this zone and summarize status, machine type, external IPs, and possible cost or exposure concerns."
- "Find reserved or external IP addresses and tell me which ones may be unused or risky."
- "Review Cloud Storage buckets and point out public access concerns if the API returns them."
- "Show Cloud Run services in this region and tell me which ones appear public, active, or worth checking next."
- "List Cloud SQL instances and summarize engine, region, backup-related fields, and public network exposure if available."
- "Review VPC networks, subnets, routes, and firewall-related resources before we touch networking."
- "Check recent logs for this service or project and summarize errors, warnings, and anything urgent."
- "Prepare a plan to disable an unused service, delete an unused IP, or update a resource, but do not apply it."

## Common jobs this helps with

### Account and project review

- confirm the project, folder, organization, billing account, quota project, and region the agent is using
- find which projects the signed-in user or service account can see
- check enabled services before asking for a larger review
- spot when the agent is in the wrong project before any change is planned

### Access and security review

- inspect IAM policies, service accounts, access-related resources, KMS areas, and security settings where permissions allow
- identify permission changes that need a plan and approval
- check whether a request may affect public exposure, identity, secrets, or logs

### Infrastructure and cost review

- review servers, disks, reserved IP addresses, networks, databases, Cloud Run services, and storage buckets
- find obvious cost areas like running machines, databases, idle IPs, quotas, and enabled services
- prepare cleanup plans without deleting the wrong thing

### Incident and operations review

- pull logs or monitoring-related data when a service is failing
- compare what is running across projects or regions
- gather enough evidence for a human to decide the next step

## What the agent should show you

- which Google Cloud identity, project, quota project, region, zone, or service it checked
- whether the result was empty, blocked by IAM, blocked by an allowlist, or surprising
- a short explanation of what matters before raw JSON
- a preview before any live change
- the approval steps needed for risky changes
- a receipt after live work, including whether verification was full or limited

## When not to use it

- Do not use it to bypass Google Cloud IAM or your normal change-review process.
- Do not use it for Google Ads, Analytics, Search Console, Merchant, Tag Manager, Workspace, YouTube, or other separate Google products.
- Do not ask it to choose a destructive target from a vague request. Ask it to identify the target and plan first.
- Do not treat local tests, generated coverage, or mocked examples as proof that your live Google Cloud account has been checked.
