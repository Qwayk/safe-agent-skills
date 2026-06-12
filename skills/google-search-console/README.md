# Google Search Console

**Capability:** Reads + careful changes

Google Search Console is where Google shows what it can see from your site: search queries, pages, indexing details, URL inspection results, and submitted sitemaps. This skill helps an agent turn that data into a clear SEO check instead of guessing from the outside.

Use it for questions like "Which sites can I access?", "What queries and pages changed in the last 28 days?", "How does Google see this URL?", or "Should we submit this sitemap after checking the current state?"

Most work is read-first: reports, URL inspection, site lists, and sitemap review. The only write-capable flows are site add or delete and sitemap submit or delete; those start as dry-run plans, and delete actions need extra irreversible approval before they can run.

A good first ask is: "Check which Search Console sites I can access, show the top queries and pages for the last 28 days, and tell me if any sitemap or indexing issue needs attention before we change anything."

## Start here first

- Want ideas for real Search Console work? [What you can do with Google Search Console](docs/use_cases.md)
- Need setup? [Connect your Google Search Console account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- List the Search Console sites your account can access.
- Run Search Analytics reports by query, page, country, device, and date range.
- Inspect a URL and summarize how Google sees its indexing status.
- Review sitemaps and prepare careful submit or delete actions.
- Add or remove site properties with plan-first safety gates.

## What access this skill needs

- A Google OAuth client secrets file or a service account file.
- The right Search Console scope for the job: read-only or read and write.
- A verified site or URL-prefix property when you want property-specific reports or URL inspection.
- Service-account access granted inside Search Console if you use the service-account path.

For most people, installed-app OAuth is the easiest starting point.

## Install and first run

Install slug: `google-search-console`

Ask your agent to install the `google-search-console` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@google-search-console -g -y
```

Then try a safe first ask like:

```text
Check which Search Console sites I can access, show the top queries and pages for the last 28 days on this property, and stop before any changes.
```

## How this skill stays safe

- It keeps one explicit command per supported Google method instead of exposing a generic raw bridge.
- Writes are dry-run first and do not run live unless you pass `--apply`.
- Write-capable flows are limited to site add or delete and sitemap submit or delete.
- Delete actions are treated as irreversible and need extra approval gates.
- Write-capable runs keep local proof under `.state/runs/` for review.
- The tool verifies after write when it can, and it should label any weaker proof honestly.

## What it covers today

This skill covers:

- auth checks and site discovery
- Search Analytics reports
- URL inspection reads
- site add and delete
- sitemap list, submit, and delete

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the site property or sitemap target before apply.
- Read work can run immediately.
- Live writes need `--apply`.
- Irreversible deletes need `--yes --ack-irreversible --plan-in`.
- After apply, the tool verifies the result and leaves a receipt or clearly labels any limit.

## What proof it leaves behind

- Dry-run output acts as the review plan for write-capable commands.
- Apply output acts as the receipt.
- Write-capable runs include `before_state`, and local artifacts can point to `before_state.json`.
- Local run history lives under `.state/runs/` when artifacts are enabled.
- The docs, tests, and API coverage notes are all in this repo.

## Limits

- Writes are intentionally limited to site add or delete and sitemap submit or delete.
- Delete actions are irreversible and need extra approval.
- You still need real Search Console access for the site or property you want to inspect.
- Service accounts are not always the easiest auth path if the property access is not set up correctly.

## Helpful docs

- [Browse all Google Search Console docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
