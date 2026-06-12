# Sovrn

**Capability:** Read-only

Sovrn helps publishers answer revenue questions across Commerce and Advertising: which campaigns are active, which merchants are approved, which pages or links are earning, and which reports are safe to pull for one publisher. This skill lets an agent inspect those Sovrn surfaces while keeping the Commerce and Advertising credential split visible.

It is useful for questions like "Can this product URL be monetized?", "Which merchant groups are approved?", "Which pages or links performed?", "Can you compare offers or coupons?", or "Which Advertising reports can this publisher pull?"

The tool is read-only against Sovrn. Even when an official Sovrn endpoint uses `POST` for a query, this tool treats it as read-only work and never changes your Sovrn account. The real risk is using the wrong key type, wrong publisher ID, or a report scope that is broader than you meant to run.

A good first ask is: "Check the Sovrn skill is configured, then show me active campaigns, approved merchant groups, and the safest Commerce or Advertising reports I can run first."

## Start here first

- Want ideas for real Sovrn work? [What you can do with Sovrn](docs/use_cases.md)
- Need setup? [Connect your Sovrn account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check Sovrn Commerce campaigns and approved merchant groups.
- Pull Commerce reports for pages, links, merchants, networks, merchandise, transactions, or CUIDs.
- Check whether a product URL can be monetized before you use it.
- Compare prices, offers, coupons, or product recommendations through the official Commerce endpoints.
- Pull Sovrn Advertising account, bid, breakout, domain, or custom reports.

## What access this skill needs

- Your Sovrn Commerce secret key for campaigns, merchant groups, and most Commerce reporting.
- Your Sovrn Commerce site API key for links checks, price comparisons, coupons, and product recommendations.
- Some Commerce command families use both Commerce values.
- Your Sovrn Advertising API key plus the matching publisher ID for Advertising reports.

## Install and first run

Install slug: `sovrn`

Ask your agent to install the `sovrn` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@sovrn -g -y
```

Then try a safe first ask like:

```text
Connect the Sovrn skill to my account, check which Commerce and Advertising credentials are ready, and show me the campaigns and reports I can run safely first.
```

## How this skill stays safe

- It is read-only to Sovrn by design.
- It uses only explicit named commands and no raw request bridge.
- It keeps the real Sovrn auth split visible instead of flattening Commerce and Advertising into one fake credential model.
- `onboarding` can create a local placeholder `.env` file, but it never fills secrets for you and it never asks you to paste secrets into chat.
- `auth check` proves local readiness only. It does not pretend to be live vendor proof.
- The docs, tests, proof pack, and API coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- local onboarding and auth checks
- Commerce campaigns and approved merchant groups
- Commerce reports for pages, links, merchants, networks, merchandise, transactions, and CUIDs
- Commerce link checks, bid checks, coupons, product recommendations, and price comparisons
- Advertising reporting commands for account, bid, breakout, domain, and custom report pulls

## What happens before a real change

This skill does not change anything inside Sovrn.

Before credentialed reads:

- the agent should run onboarding or auth check first
- you confirm which command bundle needs the Commerce secret key, the Commerce site API key, or both
- you confirm the Advertising publisher ID before Advertising report pulls
- if a needed credential is missing, the tool should say so instead of guessing

The only local change this skill can make is creating a placeholder `.env` file during onboarding.

## What proof it leaves behind

- Commands return machine-readable JSON that you can save or review.
- `auth check` shows which Sovrn command bundles are locally ready without printing secrets.
- The proof pack includes redacted example outputs for version output, local auth readiness, and a live invalid-secret Commerce response.
- Positive live-success proof still needs a real Sovrn credential set and is tracked honestly in the proof docs.

## Limits

- No remote Sovrn writes.
- Real account work still needs valid credentials, the right publisher ID, and the right key type for each command family.
- Some Commerce product areas may still depend on vendor-side access or account enablement.
- `auth check` is only a local setup check. Live vendor proof still comes from the real Commerce or Advertising read commands.

## Helpful docs

- [Browse all Sovrn docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
