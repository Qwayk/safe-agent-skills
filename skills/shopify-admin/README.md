# Shopify Admin SafeCLI (`shopify-admin-api-tool`)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first, explicit-command CLI for the Shopify **Admin GraphQL API**.

Pinned API version: **2026-01** (inventory + command surface are derived from Shopify’s official docs for this version).

Mutation commands are plan-first. They generate review plans, and live apply requires explicit no-snapshot approval before Shopify HTTP when no operation-specific saved snapshot is available.

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Skills wrappers (required for customer-ready tools): `docs/skills_wrappers.md`
- Coverage ledger (“100%” mapping): `docs/api_coverage.md`

Examples of what you can ask your agent (plain English, no commands):

- “Create a new product with these variants and prices, but show me a dry-run preview first.”
- “Draft a plan to update prices for these SKUs by 10%, and show what would be sent.”
- “Pull all orders from the last 30 days and export them to a JSON file.”
- “Find customers who match this segment, then export their IDs to a file.”
- “Create a dry-run plan for a discount code with these rules, and tell me why live apply requires explicit no-snapshot approval today.”

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
shopify-admin-api-tool --version
shopify-admin-api-tool onboarding
shopify-admin-api-tool auth check
shopify-admin-api-tool operations list
shopify-admin-api-tool --output json query shop
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`
