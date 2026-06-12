# Amazon Creators

**Capability:** Reads + guarded local helpers

Amazon Creators is useful when you need structured Amazon catalog details for books, media formats, browse nodes, variations, and marketplace locales before making content or catalog decisions.

This skill helps an agent look up ISBNs or ASINs, compare media formats, inspect browse-node context, search catalog results, and confirm locale/resource choices before a live catalog request is sent.

Use it for questions like: "What formats exist for this book?", "Which parent ASIN connects these variations?", "What browse-node path describes this niche?", "Which locale should this request use?", or "Can you show the dry-run plan before calling Amazon?"

Remote catalog work is read-only against Amazon, but catalog requests are still preview-first. Local helpers that create `.env` files or write token state also plan first and need explicit no-snapshot approval when no saved before-state exists.

A good first ask is: "Check the Amazon Creators setup, show the supported locales and resource presets, dry-run an item lookup for this ISBN, and wait for approval before calling Amazon."

## Start here first

- Want ideas for real Amazon Creators work? [What you can do with Amazon Creators](docs/use_cases.md)
- Need setup? [Connect your Amazon Creators account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Describe browse nodes.
- Get item details for ISBNs or ASINs.
- Get variation details and parent-child relationships.
- Search Amazon Creators catalog data.
- Expand high-level locale and resource presets into Amazon's concrete resource enums.
- Keep request plans, receipts, and run history for review.

## What access this skill needs

- Amazon Creators credentials and locale settings.
- Token endpoint settings that match the credential version and locale.
- Approval before a dry-run catalog plan is sent to the live API.
- Local no-snapshot approval before helper commands write `.env` or token-cache state when no before-state is saved.

## Install and first run

Install slug: `amazon-creators`

Ask your agent to install the `amazon-creators` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@amazon-creators -g -y
```

Then try a safe first ask like:

```text
Check the Amazon Creators setup, show the supported locales and resource presets, dry-run an item lookup for this ISBN, and wait for approval before calling Amazon.
```

## How this skill stays safe

- Catalog commands are read-only against Amazon.
- Catalog commands run as dry-run plans by default and only call Amazon after `--apply`.
- Local onboarding and token helpers plan first.
- Local file or token-cache writes need explicit no-snapshot approval when no saved before-state is available.
- Plans, receipts, and audit logs must not include secrets.

## What it covers today

This skill covers the audited public Creators Catalog scope from Issue #404:

- `browse-nodes describe`
- `items get`
- `variations get`
- `search`
- locale helpers that expand high-level resource presets into Amazon resource enums

## What happens before live work

- The agent should show the dry-run plan first.
- You review the locale, marketplace resources, identifiers, and request parameters.
- Catalog API calls need approval with `--apply`.
- Local helper writes need no-snapshot approval when no saved before-state is available.
- After catalog apply, the agent returns simplified data plus a receipt.

## What proof it leaves behind

- Dry-run plans show the operation, locale, resources, and request payload.
- Catalog apply receipts show request details, outcome, verification, and local artifact paths.
- Run history can record plans, receipts, and logs.
- The docs, tests, examples, proof pack, and API coverage ledger live in this repo.

## Limits

- The shipped surface is the audited Creators Catalog scope, not every Amazon API.
- `--plan-in` is reserved and has no effect on this shipped surface.
- Local helper writes have no automatic restore path unless a saved before-state exists.
- Catalog results depend on locale, credentials, and what Amazon returns for the requested identifiers.

## Helpful docs

- [Browse all Amazon Creators docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
