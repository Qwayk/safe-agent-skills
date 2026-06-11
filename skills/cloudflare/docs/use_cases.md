# Use cases

Use this page when you want ideas for real Cloudflare jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## What this tool is for (today)

This tool helps you safely **inventory** and (with explicit approval) make controlled changes to your Cloudflare setup:
- Accounts and Zones discovery
- DNS records inventory + safe single-record writes (plan-first) + sensitive export/import (file-only)
- Workers scripts (metadata only) + script extras (schedules/settings/usage model/subdomain/secrets metadata)
- Worker routes (zone-scoped)
- Workers Dispatch namespaces/scripts (metadata only; no script content) + bindings/tags/secrets metadata
- Workers for Platforms dispatch writes (create/update namespace, upload/update customer Workers, tags, secrets) via explicit per-operation `operations` commands (safe-by-default)
- Workers KV namespaces and key metadata (never KV values)
- Workers versions, deployments, and tails (GET only; no streaming)
- Workers account settings, placement regions, and Workers for Platforms inventory
- Workers builds and pipelines (GET only; includes legacy/deprecated GETs)
- Safe write workflows (preview-first; require explicit “apply” approval): Workers routes, Workers subdomain, Workers domains
- Sensitive reads to file (extra confirmation; file output only): Workers script download/content, KV values
- Zero Trust read-only inventory (selected surfaces): org, gateway rules/lists/config/logging, devices, access apps/policies
- Full Zero Trust coverage (including DLP) via explicit per-operation `operations` commands (plan-first writes; file-only for sensitive outputs)

If you need a configuration change that doesn’t have a “named” command yet, your agent can still do it safely using the tool’s advanced full-coverage mode (plan-first writes, file-only sensitive outputs).

## Why this beats typical no-code automation

Most “automation” tools make it hard to answer a simple question: “What exactly will change?”

This tool is designed for safe, reviewable changes:
- **Preview-first**: the agent can produce a deterministic plan before anything changes.
- **Explicit approval**: nothing writes until you approve the apply step.
- **Verification**: after a change, the tool re-checks the API to confirm the expected state.
- **Receipts**: you get a saved receipt you can audit or share with a reviewer (without exposing secrets).
- **Bulk-ready**: you can plan many small changes, review them, then apply safely and consistently.

## Common use cases (examples)

- “List my Cloudflare accounts and set my default account id.”
- “List all DNS records for a zone, then plan an update for one record (apply only after I approve).”
- “Export my zone’s DNS records to a local file (don’t print the zonefile).”
- “Plan a DNS import, show me the plan, and only apply after I approve (bulk write).”
- “Review my DNSSEC status for a zone and plan a change (apply only after I approve).”
- “List my Secondary DNS TSIGs and save the result to a local file (don’t print secrets).”
- “Plan enabling outgoing zone transfers for a zone, then apply after I approve.”
- “Inventory all Workers scripts in my account (names, metadata/settings).”
- “Show me script cron schedules and usage model for a given Worker.”
- “Resolve my zone id and list all Worker routes for that zone.”
- “Plan a new Worker route mapping (pattern → script), then apply it after I approve.”
- “Ensure a Worker route is removed (with a preview plan first; apply only after I approve).”
- “Download one Worker script to a local file for review (never print content).”
- “Read a single KV value to a file for offline inspection (never print the value).”
- “Start an assets upload session for a Worker and save the temporary upload token to a local file (never print it).”
- “Create a dispatch namespace for customer Workers and upload a first customer Worker (plan first, apply only after I approve).”
- “List my Zero Trust Gateway rules and fetch one by id.”
- “List my DLP profiles/datasets so I can review my data-loss-prevention setup.”
- “Plan a Zero Trust policy change (Access/Gateway/DLP), then apply it only after I approve.”
- “List Workers for Platforms workers and fetch one by worker id.”
- “List pipelines/streams/sinks to see what data pipelines exist in this account.”
- “List KV namespaces and key metadata (size, last modified, etc.) without reading any values.”
- “List Workers versions and deployments for a given script.”
- “List my Cloudflare user profile / organizations / memberships and save the results to a local file (don’t print PII).”
- “List my user API tokens, verify a token, or roll a token value (save any secret-bearing results to a local file; requires explicit acknowledgement).”
- “List my organization members and plan adding/removing a member (apply only after I approve; destructive actions require extra acknowledgement).”
- “Create an Origin CA certificate and save it to a local file (never print private key material).”
- “Search stored logs/events by Error ID and save the results to a local file (never print log contents).”

## What you’ll see from the agent (trust + safety)

When you ask for an inventory task, the agent should:

1) Confirm the tool is connected (a safe, read-only connection check).
2) Ask for (or discover) the right IDs (account id, zone id, script name).
3) Run the read-only command(s) and return structured output.
4) For any write or sensitive-read request: produce a preview plan (or a preview summary) first and only proceed after you explicitly approve the apply step.
