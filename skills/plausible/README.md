# Plausible

**Capability:** Reads + careful changes

Use this skill when you want your agent to answer real Plausible questions without guessing from raw docs.

You can hand your agent jobs like weekly traffic and conversion reports, Stats query validation, signup or membership funnel analysis, and careful site or event changes.

Read work stays simple. Riskier work slows down on purpose: site changes start as dry-run plans, destructive actions need extra approval, and event sends need explicit approval because they write analytics data that cannot be undone automatically.

A good first ask is: "Show me what changed in traffic, sources, and goal conversions over the last 7 days."

## Start here first

- Want ideas for real Plausible work? [What you can do with Plausible](docs/use_cases.md)
- Need setup? [Connect your Plausible account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Run weekly or monthly Plausible reports for traffic, sources, devices, and goals.
- Validate Stats API queries before running them.
- Build funnel and comparison reports for membership or conversion work.
- Review sites, goals, custom properties, guests, and shared links.
- Plan careful analytics changes or test events before anything is sent.

## What access this skill needs

- A Plausible API key.
- Your site ID or domain.
- If you self-host Plausible, your base URL.
- Some destructive site changes may need an owner key for that site.

## Install and first run

Install slug: `plausible`

Ask your agent to install the `plausible` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@plausible -g -y
```

Then try a safe first ask like:

```text
Connect the Plausible skill to my account and show me the top pages, sources, and goal conversions from the last 7 days.
```

## How this skill stays safe

- Read-only reporting and query validation do not write anything.
- Site and analytics writes start as dry-run plans first.
- Live changes need explicit apply flags, and destructive actions need extra acknowledgement.
- `event send` writes analytics data and cannot be undone automatically, so it also needs explicit no-snapshot approval.
- Event verification is best-effort only; Plausible does not offer an exact read-back for one specific event.
- Plans, receipts, docs, tests, and code all live together so you can inspect what the agent is using.

## What it covers today

This skill covers:

- Stats API queries and reports
- funnel, comparison, and goal analysis
- site reads
- site writes for create, update, delete, goals, custom properties, guests, and shared links
- careful event sends with explicit approval

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target, payload, and risk.
- Safe reads can run immediately.
- Site writes need `--apply --yes`.
- Destructive actions need `--ack-irreversible`.
- Writes without a saved before-state, like `event send` and `site shared-links ensure`, also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Many site writes include before-state details when the API makes that possible.
- `event send --verify` can do a best-effort check when you use a unique URL path.
- The docs, tests, and coverage ledger are all in this repo.

## Limits

- `event send` cannot be undone automatically.
- Event verification is best-effort, not exact replay proof.
- `event send` and `site shared-links ensure` do not have saved before-state because Plausible does not expose the exact prior state needed.
- You still need valid Plausible access for real account work.

## Helpful docs

- [Browse all Plausible docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
