# Skimlinks

**Capability:** Read-only

Use this skill when you want your agent to inspect Skimlinks merchants, reporting, Product Key lookups, and Link Wrapper URLs without guessing from raw docs.

You can hand your agent jobs like merchant discovery for a country or category, commission and page/link reports, Product Key alternative checks, and Link Wrapper URL builds for links that need monetizing outside browser JavaScript.

This skill stays read-only against Skimlinks on purpose. Merchant, Reporting, and Product Key commands only read or query official Skimlinks surfaces. Link Wrapper only builds the official monetized URL locally and does not open it.

A good first ask is: "Check the Skimlinks skill is configured, then show me active merchants and top commission links for last month."

## Start here first

- Want ideas for real Skimlinks work? [What you can do with Skimlinks](docs/use_cases.md)
- Need setup? [Connect your Skimlinks account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Find merchants, domains, verticals, alternative verticals, and offers for a market or brand.
- Pull commission, aggregated, link, page, trending-product, and payment-status reports.
- Check Product Key details or alternatives for one product or many products.
- Build official Link Wrapper URLs for links that need monetizing outside browser JavaScript.
- Verify which credentials and publisher IDs are ready before a live read.

## What access this skill needs

- Merchant API and Reporting API client credentials plus your Skimlinks publisher ID.
- A publisher domain ID for Product Key lookups.
- Product Key may need separately enabled credentials from Skimlinks.
- A Link Wrapper ID if you want a default ID for Link Wrapper builds.

## Install and first run

Install slug: `skimlinks`

Ask your agent to install the `skimlinks` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@skimlinks -g -y
```

Then try a safe first ask like:

```text
Connect the Skimlinks skill to my account, check my credentials, and show me the top commission links and active merchants for last month.
```

## How this skill stays safe

- It does not send remote Skimlinks writes.
- It uses only explicit named commands and no raw request bridge.
- Product Key credential limits stay visible instead of being hidden behind the shared auth path.
- Link Wrapper builds the official monetized URL locally and does not click it or follow redirects.
- `onboarding` can create a local placeholder `.env` file, but it never fills secrets for you and it never asks you to paste secrets into chat.
- The docs, tests, proof pack, and API coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- Merchant API reads for merchants, domains, verticals, alternative verticals, and offers
- Reporting API reads for commissions, aggregated reports, link reports, page reports, trending products, product reports, payment status, and deactivated merchants
- Product Key single-product and multi-product lookups
- Link Wrapper URL builds
- local onboarding and auth checks so you can verify setup before real account reads

## What happens before a real change

This skill does not change anything inside Skimlinks.

Before credentialed reads:

- the agent should run onboarding or auth check first
- you confirm the publisher ID and, for Product Key, the publisher domain ID
- if Product Key is not enabled, the tool should say so instead of guessing

The only local changes this skill can make are creating a placeholder `.env` file during onboarding and printing a Link Wrapper URL for you to reuse elsewhere.

## What proof it leaves behind

- Commands return machine-readable JSON that you can save or review.
- `auth check` proves whether the local setup is ready without printing secrets.
- When a command creates local run artifacts, they live under `.state/runs/`.
- The proof pack includes redacted example outputs, tests, and the API coverage ledger.

## Limits

- No Merchant, Reporting, Product Key, or Link Wrapper remote writes.
- Product Key can still be unavailable even when normal Merchant or Reporting credentials work.
- Data Pipe and Skimlinks JavaScript are official Skimlinks areas, but they are documented only and not shipped as CLI command families here.
- Real account work still needs valid credentials, the right publisher ID, and the right publisher domain ID when Product Key is involved.

## Helpful docs

- [Browse all Skimlinks docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
