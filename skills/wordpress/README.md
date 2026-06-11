# WordPress

**Capability:** Reads + careful changes

Use this skill when you want your agent to review WordPress posts, pages, media, categories, tags, comments, and migration data without guessing from raw docs.

You can hand your agent jobs like content audits, featured-image gap checks, media metadata cleanup, careful caption or taxonomy edits, bulk media download plans, and migration prep across large content libraries.

Read work stays simple. Riskier work slows down on purpose: content and media edits start as dry-run plans, applies verify by read-back or idempotence, and some batch write paths are not available for live use yet because the tool still needs safer per-row before-state.

A good first ask is: "Check the WordPress skill is connected, list recent posts and pages, show featured-image gaps, and stop before any edits."

## Start here first

- Want ideas for real WordPress work? [What you can do with WordPress](docs/use_cases.md)
- Need setup? [Connect your WordPress site](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review posts, pages, media items, comments, search results, categories, and tags across a live WordPress site.
- Audit content gaps like missing featured images, weak captions, missing alt text, or taxonomy cleanup work.
- Plan careful edits for media metadata, visible image captions, exact content replacements, post status changes, and taxonomy assignments.
- Generate migration tracking CSV files from WordPress export XML.
- Use optional read-only admin surfaces like users and settings when the site permissions allow them.

## What access this skill needs

- Your WordPress site base URL.
- A dedicated WordPress user with an Application Password.
- The lowest role that can do the job, usually Author or Editor before Administrator.
- Extra permissions only when you truly need read-only admin surfaces like users or settings.

## Install and first run

Install slug: `wordpress`

Ask your agent to install the `wordpress` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@wordpress -g -y
```

Then try a safe first ask like:

```text
Check the WordPress skill is connected, list recent posts and pages, show featured-image gaps, and stop before any edits.
```

## How this skill stays safe

- Content and media writes stay dry-run first and do nothing live unless you add `--apply`.
- The main media and post edit commands save the current target state under `.state/runs/<run-id>/before/` before apply.
- Applies verify by read-back or idempotence instead of assuming success.
- Exact targeting and slug-based term resolution refuse when the target is missing or ambiguous.
- Batch paths need stronger gates like `--apply --yes`, and the batch runner is not available for live writes yet because safer per-row restore is still missing.
- Plans, receipts, before-state files, docs, tests, and the API coverage ledger all live in this repo.

## What it covers today

This skill covers:

- post and page discovery, truth views, image extraction, comments, search, and taxonomy review
- media metadata updates and batch local media download planning
- safe post edits for image captions, exact replacements, taxonomy terms, and status changes
- migration tracking from WordPress export XML

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target posts, pages, media items, or local download plan before apply.
- Normal content and media writes need `--apply`.
- Batch local writes like `media download-batch` need `--apply --yes`.
- Batch `jobs run` writes can still refuse until safer per-row restore is available.
- Successful applies verify by read-back or idempotence and report the result.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Supported edit families save before-state under `.state/runs/<run-id>/before/`.
- Apply output reports the verification result for the change that ran.
- The docs, tests, proof pack, and API coverage ledger are all in this repo.

## Limits

- This skill is for content and migration workflows, not full site administration.
- It does not manage plugins, themes, menus, global styles, or site-wide settings writes.
- The batch runner write mode is not available yet because safer per-row restore is still missing.
- Rollback stays manual even when before-state is saved for supported edit families.

## Helpful docs

- [Browse all WordPress docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
