# Dynadot

**Capability:** Reads + careful changes

Use this skill when you want your agent to review Dynadot domains, pricing, transfers, auctions, and account settings without guessing from raw docs.

You can hand your agent jobs like expiring-domain checks, name server audits, bulk push planning, guided account-to-account transfers, and careful Dynadot changes across many domains.

Read work stays simple. Riskier work slows down on purpose: writes start as dry-run plans, bulk jobs keep pacing controls, and live Dynadot writes need explicit no-snapshot approval because this tool cannot save a real restore point for those write families yet.

A good first ask is: "Check the Dynadot skill is connected, list my active domains, flag anything expiring soon, and show me the safest next step before any changes."

## Start here first

- Want ideas for real Dynadot work? [What you can do with Dynadot](docs/use_cases.md)
- Need setup? [Connect your Dynadot account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review your domain inventory, balances, coupons, transfers, orders, contacts, DNS, and current name servers.
- Check pricing, marketplace listings, auctions, closeouts, backorders, and CN audit status.
- Plan bulk pushes between Dynadot accounts.
- Plan bulk name server changes with diffs, pacing, and read-back verification.
- Preview privacy, forwarding, renewal, folder, and other API3 changes before anything goes live.

## What access this skill needs

- A Dynadot API key.
- Optional IP whitelist support if you want to lock the key down further in Dynadot.
- A receiver push username for domain pushes.
- Two local `.env` files when you run the guided sender-to-receiver transfer workflow.
- Transfer auth codes should stay in local files because they are sensitive.

## Install and first run

Install slug: `dynadot`

Ask your agent to install the `dynadot` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@dynadot -g -y
```

Then try a safe first ask like:

```text
Connect the Dynadot skill, list my active domains, flag anything expiring in the next 60 days, and preview the safest next step before any changes go live.
```

## How this skill stays safe

- It does not expose a generic raw-call bridge.
- Writes start as dry-run plans first.
- Live writes need a reviewed plan, `--apply`, and `--yes`.
- Monetary or irreversible actions also need `--ack-irreversible`.
- Dynadot write families still do not have saved before-state here, so live apply also needs `--ack-no-snapshot`.
- Bulk workflows keep batching, pacing, verification, and receipt support so large runs stay reviewable.

## What it covers today

This skill covers:

- account, pricing, marketplace, auction, closeout, backorder, transfer, order, contact, and DNS reads
- bulk domain pushes between Dynadot accounts
- guided sender-to-receiver transfer runs
- name server exports, diffs, and bulk set plans
- first-class API3 coverage for every official request-example command in Dynadot's published docs

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the domains, target account, and any money or irreversible risk before apply.
- Safe reads can run immediately.
- Live writes need `--apply --yes --plan-in`.
- Monetary or irreversible actions also need `--ack-irreversible`.
- Dynadot writes without a saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Large runs can resume from earlier receipts when the command supports it.
- Run history is written under `.state/runs/` next to your local env file.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Dynadot write families still do not have automatic restore points here.
- Some actions are monetary or otherwise irreversible and need extra acknowledgement.
- Pushes and guided transfers depend on the correct receiver push username and the right account credentials.
- Transfer auth codes are sensitive and should not be pasted into chat or tickets.

## Helpful docs

- [Browse all Dynadot docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
