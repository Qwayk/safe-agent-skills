# Fortnox

Fortnox is where many teams keep invoices, supplier bills, bookkeeping, payroll, and stock in one place. This skill gives your AI agent a careful way to check that work, review changes before it sends, books, updates, or deletes records, and leave proof behind after it runs.

A good first ask is: "Check that Fortnox is connected, show our company details, list a few customers and invoices, and tell me which change should be planned instead of applied live."

## Start here first

- Want plain-English ideas first? [What you can ask the Fortnox skill to do](docs/use_cases.md)
- Need setup help? [Set up your Fortnox connection step by step](docs/onboarding.md)
- Want the safety story first? [Read the Fortnox safety guide](docs/safety_model.md)
- Want the first safe command flow? [Do the first safe Fortnox check](docs/quickstart.md)
- Need the full command list? [Open the technical command guide](docs/command_reference.md)

## What this skill helps with

- Check company details, customers, suppliers, invoices, supplier invoices, prices, accounts, warehouse data, payroll, and time records.
- Review official Fortnox websocket topics when you need tenant or event visibility.
- Prepare changes as reviewed plans before creating, updating, booking, sending, or removing records.
- Keep accounting and bookkeeping work explicit instead of letting an agent guess from raw API docs.

## What access this skill needs

- A Fortnox integration with a client ID, client secret, and redirect URI.
- A local `.env` file for those private values.
- Normal OAuth approval for the tenant you want to use.
- An optional service-account tenant ID when your Fortnox setup uses that official flow.

## Install and first run

Install slug: `fortnox`

Ask your agent to install the skill from `Qwayk/safe-agent-skills`.

If auto-install is not available, run:

```bash
npx skills add Qwayk/safe-agent-skills@fortnox -g -y
```

Then try a safe first ask like:

```text
Check that Fortnox is connected, show our company details, list a few customers and invoices, and tell me which change should be planned instead of applied live.
```

When access is needed, run onboarding first. It will show which local Fortnox app values are missing without printing secrets.

## How this skill stays safe

- Reads work without any live-write approval.
- Writes start as dry-run plans.
- Real writes require `--apply --yes --plan-in`.
- High-risk writes with no useful before-state snapshot also require `--ack-no-snapshot`.
- Clearly irreversible writes also require `--ack-irreversible`.
- Apply paths verify after the change and leave a local receipt.

## What it covers today

- This skill includes explicit commands for the currently mapped official Fortnox REST and websocket surface.
- The strongest coverage today is in accounting, bookkeeping, invoices, supplier flows, warehouse records, payroll/time, document intake, and attachment families.
- Common accounting reads now keep the rendered Fortnox list filters explicit on the CLI where the docs show them, instead of hiding them behind a generic query passthrough.
- The local code and tests are in place for the shipped surface, but live Fortnox account checks were not run here because no real Fortnox credentials were available during validation.

## What happens before live changes

- The agent picks one explicit Fortnox command family and one clear target.
- The tool can save a dry-run plan so you can review the exact payload first.
- Apply reuses that reviewed plan instead of rebuilding the change from scratch.
- When Fortnox does not offer a useful before-state snapshot or easy undo path, the tool says that plainly before it will proceed.

## What proof it leaves behind

- Saved plan files when you ask for them.
- Receipts that record verification, snapshot status, and recovery notes.
- Follow-up reads or other checks that confirm the change landed.
- Local logs and examples you can inspect later during review.

## Limits

- `jobs run` stays unsupported until real registry-backed Fortnox job rows exist.
- This skill only covers the official documented Fortnox surface mapped here.
- Live Fortnox account behavior remains unverified from this validation run because real Fortnox credentials were not available.

## Helpful docs

- [Browse all Fortnox docs](docs/README.md)
- [Do the first safe Fortnox check](docs/quickstart.md)
- [Open the technical command guide](docs/command_reference.md)
- [Read the Fortnox safety guide](docs/safety_model.md)
- [See proof and verification](docs/proof.md)
- [Inspect the full API coverage ledger](docs/api_coverage.md)
