# Use cases

Use this page when you want ideas for real Ghost jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with a live Ghost site

Ghost work is usually not one simple trigger. It often means reviewing a live content library, planning changes carefully, and keeping proof of what changed:

- Bulk analysis and exports (hundreds/thousands of posts)
- Preview-first workflows (dry-run → explicit apply → verification)
- Deterministic behavior (refuses when unsure instead of guessing)
- Proof artifacts (plans/receipts/logs and backups) you can keep for auditing

## Common use cases (examples)

### Content discovery and reporting

- “Give me a report of my posts: status, publish dates, authors, tags, and reading time.”
- “Export email delivery stats for my posts so I can see what was sent and what performed.”
- “Find posts missing key metadata (title/description/featured image) and list them.”
- “List my public posts/pages/tags using the Content API (read-only, no Admin key) so I can build a sitemap or audit what’s visible.”

### Site audits (read-only)

- “Audit internal links and show me broken links, orphans, and candidate hub pages.”
- “Audit tags: find duplicates, unused tags, and suspicious tag sprawl.”
- “Audit author attribution across posts and produce a clean report.”

### Membership / newsletter operations (careful)

- “Export member engagement so I can understand retention and activity.”
- “Preview changes to member labels or newsletter subscriptions; apply only after I approve.”

### Membership pricing and promotions (careful)

- “List my membership tiers and summarize what’s public vs hidden.”
- “Create a new tier or update pricing/benefits, but only after I approve a preview.”
- “Create or update an offer (like a seasonal discount) and keep a local receipt so we can update or delete it later.”

### Safe cleanups (explicit approval)

- “Preview deleting tags that have zero posts (no changes until I approve).”

### Site operations (high-impact)

- “Upload a new theme zip and show me what would change before activating it.”
- “Set up a webhook for a specific event, but treat it as high-risk because Ghost doesn’t let us list webhooks later.”

## What you’ll see from the agent (trust + safety)

When you ask for changes, the agent should:

1) Show a dry-run preview of what would change.
2) Apply only after explicit confirmation (and extra confirmations for destructive actions).
3) Verify after apply (read-back).
4) Provide a short receipt and point to saved proof artifacts and backups.
