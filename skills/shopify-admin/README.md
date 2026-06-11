# Shopify Admin

**Capability:** Reads + careful changes

Use this skill when you want your agent to review Shopify products, variants, inventory, orders, customers, discounts, collections, and other Admin API work without guessing from raw docs.

You can hand your agent jobs like product and inventory reviews, order exports, customer segment pulls, discount plans, bulk metadata updates, and careful Shopify mutations that should be previewed before they touch the store.

Read work stays simple. Riskier work slows down on purpose: Shopify mutations start as dry-run plans, higher-risk mutation families need stronger approval gates, and live apply still needs explicit no-snapshot approval when no operation-specific saved snapshot is available.

A good first ask is: "Check the Shopify Admin skill is connected, list the store details, export my recent orders and product list, and stop before any mutations."

## Start here first

- Want ideas for real Shopify work? [What you can do with Shopify Admin](docs/use_cases.md)
- Need setup? [Connect your Shopify Admin account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review shop details, products, variants, inventory, orders, customers, collections, and discounts.
- Export Shopify data for reporting or cleanup work.
- Build careful product, pricing, inventory, discount, and metadata mutation plans.
- Show the exact risk gates for Shopify mutations before any live apply.
- Work across the pinned Shopify Admin GraphQL surface with explicit top-level query and mutation commands.

## What access this skill needs

- Your shop domain.
- A Shopify custom app Admin API access token.
- The pinned Shopify Admin API version.
- The right read or write scopes for the store work you want to do.

If you only need reviews or exports, start with read scopes first.

## Install and first run

Install slug: `shopify-admin`

Ask your agent to install the `shopify-admin` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@shopify-admin -g -y
```

Then try a safe first ask like:

```text
Check the Shopify Admin skill is connected, list the store details, export my recent orders and product list, and stop before any mutations.
```

## How this skill stays safe

- It keeps explicit top-level query and mutation commands instead of exposing a raw GraphQL bridge.
- Mutations stay dry-run first and do not reach Shopify unless you pass the required apply flags.
- Higher-risk mutation families need stronger risk gates like `--yes` and `--plan-in`.
- Irreversible mutation families need `--ack-irreversible`.
- When no operation-specific saved snapshot exists, live mutation apply still needs explicit `--ack-no-snapshot`.
- `--return-shape-file` stays separately gated because it can expose PII.

## What it covers today

This skill covers:

- explicit Shopify Admin GraphQL queries and mutations from the pinned API version
- read and export work for store, catalog, order, customer, and discount review
- plan-first Shopify mutations with deterministic risk classification
- plan, receipt, and run-artifact proof for Shopify work

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target resources, mutation shape, and recovery limit before apply.
- Read-only queries can run immediately.
- Normal mutations need `--apply`.
- Higher-risk mutations need `--apply --yes --plan-in`.
- Irreversible mutations also need `--ack-irreversible`.
- When no saved snapshot exists for that operation, live mutation apply also needs `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run output acts as the review plan.
- Apply output acts as the receipt.
- Local run history lives under `.state/runs/` when artifacts are enabled.
- Plans, receipts, and refusal summaries can be saved locally for review.
- The docs, tests, and API coverage ledger are all in this repo.

## Limits

- This tool does not promise automatic rollback or restore.
- Stdout is not guaranteed to be redacted, so treat Shopify query and plan output as sensitive.
- Custom return shapes can expose PII, which is why `--return-shape-file` stays separately gated.
- Live Shopify mutation apply still depends on explicit no-snapshot approval when no saved snapshot exists for that operation.

## Helpful docs

- [Browse all Shopify Admin docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
