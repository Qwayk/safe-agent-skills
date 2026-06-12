# WooCommerce

**Capability:** Reads + careful changes

WooCommerce is where a WordPress store keeps the pieces customers notice first: products, orders, customers, coupons, taxes, shipping, payment gateways, and store settings.

This skill helps an agent review store data, check catalog and order details, inspect settings, and prepare change plans before anything touches the live shop.

Use it for questions like: "Which products are active?", "What happened with this order?", "Which payment gateways are enabled?", "Can you preview this coupon?", or "Can you check shipping zones before we change them?"

Most commands need a store URL and WooCommerce REST key pair. Writes are preview-first, and live apply needs a reviewed plan plus explicit no-snapshot approval when no operation-specific before-state is available.

A good first ask is: "Check the WooCommerce connection, list products and payment gateways, show the shipping zones, and stop before any writes."

## Start here first

- Want ideas for real WooCommerce work? [What you can do with WooCommerce](docs/use_cases.md)
- Need setup? [Connect your WooCommerce store](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review products, orders, customers, coupons, reports, taxes, shipping zones, payment gateways, and store settings.
- Inspect reference data such as countries, continents, and currencies.
- Prepare preview plans for products, coupons, customers, reviews, webhooks, settings, and batch endpoint work.
- Check store data before a catalog, coupon, shipping, or admin change.
- Keep local proof files for plans, refusals, receipts, and run history.

## What access this skill needs

- Your WooCommerce store URL.
- WooCommerce REST API consumer key and consumer secret.
- HTTPS REST key auth by default.
- Optional query-string auth only when a server strips the normal `Authorization` header.

This tool covers the official WooCommerce REST API v3 under `/wp-json/wc/v3/`. It does not cover the Store API, legacy `wc/v1` or `wc/v2`, WordPress core `/wp-json/wp/v2`, or extension-only APIs.

## Install and first run

Install slug: `woocommerce`

Ask your agent to install the `woocommerce` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@woocommerce -g -y
```

Then try a safe first ask like:

```text
Check the WooCommerce connection, list products and payment gateways, show the shipping zones, and stop before any writes.
```

## How this skill stays safe

- Read commands run immediately after valid access is available.
- Writes never apply by default.
- A write without `--apply` returns a dry-run plan.
- Apply requests use `--apply --plan-in`.
- High-risk writes also need `--yes`.
- When no useful before-state can be saved, live apply requires explicit no-snapshot approval before WooCommerce HTTP.

## What it covers today

This skill covers the official WooCommerce REST API v3 areas mapped in the API coverage file, including:

- products, product variations, reviews, orders, customers, coupons, taxes, reports, and refunds
- payment gateways, shipping zones, shipping methods, settings, webhooks, and system status
- batch endpoint planning for supported WooCommerce v3 resources
- reference data such as countries, continents, and currencies

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the store, target resource, request body, and recovery limit.
- Live apply needs a reviewed plan.
- High-risk changes such as deletes, batch endpoints, order email actions, payment gateway updates, webhook writes, shipping zone location updates, and system status tool runs need stronger approval.
- If no before-state can be saved, live apply also needs explicit no-snapshot approval.

## What proof it leaves behind

- Dry-run plans can be saved for review.
- Approved supported writes can leave receipts.
- Local run history can include the plan, audit log, and run summary.
- The docs, tests, proof pack, and API coverage ledger live in this repo.

## Limits

- Store access depends on valid WooCommerce REST keys and the permissions attached to those keys.
- Some servers require query-string auth because they strip `Authorization` headers.
- The HTTP-only OAuth 1.0a flow is not shipped here.
- The tool does not promise automatic rollback, provider backups, or snapshots for every write path.

## Helpful docs

- [Browse all WooCommerce docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
