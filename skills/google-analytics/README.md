# Google Analytics

**Capability:** Reads + careful changes

Use this skill when you want your agent to pull GA4 reports, inspect account and property setup, review access, and plan careful Google Analytics admin changes without guessing from raw docs.

You can hand your agent jobs like property audits, last-7-days report checks, audience and conversion reviews, custom definition checks, data stream reviews, and careful GA4 admin changes.

Read work stays simple. Riskier work slows down on purpose: reports and discovery reads can run live, write-capable commands start as dry-run plans, and many GA4 writes need explicit no-snapshot approval because this tool does not yet save useful before-state for those changes.

A good first ask is: "Check the Google Analytics skill is connected, list the accounts and properties I can access, and show me the safest report or review steps to start with."

## Start here first

- Want ideas for real Google Analytics work? [What you can do with Google Analytics](docs/use_cases.md)
- Need setup? [Connect your Google Analytics access](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Run GA4 reports and metadata reads from the Analytics Data API.
- Review accounts, properties, data streams, access bindings, and change history.
- Check audiences, conversion events, custom dimensions, custom metrics, and other property settings.
- Review product links like BigQuery, Firebase, AdSense, and Display & Video 360 connections.
- Plan careful Analytics Admin changes before anything goes live.

## What access this skill needs

- Google credentials stored locally in `.env`.
- Access to the GA4 accounts or properties you want to inspect or change.
- Property IDs or resource names for many report and admin requests.
- Higher permissions for any admin changes you want to plan or apply.

## Install and first run

Install slug: `google-analytics`

Ask your agent to install the `google-analytics` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@google-analytics -g -y
```

Then try a safe first ask like:

```text
Connect the Google Analytics skill, list the accounts and properties I can access, and show me a simple safe report or review path for the last 7 days.
```

## How this skill stays safe

- Read-like reports and discovery commands can run live right away.
- Write-capable commands start as dry-run plans first.
- Higher-risk work can require extra confirmation flags like `--yes`, `--plan-in`, or `--ack-irreversible`.
- When GA4 does not expose useful before-state for a write, live apply also needs `--ack-no-snapshot`.
- Measurement Protocol secrets and other sensitive values stay redacted in plans, receipts, logs, and stdout.
- The docs, tests, coverage notes, and source code are all here in one place.

## What it covers today

This skill covers:

- Analytics Data API reports and metadata reads
- Analytics Admin API account and property review
- access reports and access-binding review
- audiences, conversion events, custom definitions, data streams, and property settings
- plan, review, and apply flows for write-capable GA4 admin commands
- local run history and batch jobs for repeatable work

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the account, property, target, payload, and recovery limits.
- Safe reads can run immediately.
- Write-capable commands need `--apply`.
- Higher-risk or batch apply can also require `--yes` and `--plan-in`.
- Irreversible actions also need `--ack-irreversible`.
- GA4 writes without saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Missing-approval refusals stop before the live GA4 write and leave a clear refusal instead of a fake success.
- Local run history can be reviewed with `runs list` and `runs show`.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Many GA4 writes still do not have saved before-state or a built-in undo path.
- Some apply paths depend on extra permissions, reviewed plans, and explicit no-snapshot approval.
- Live coverage follows the vendored GA4 discovery snapshots in this repo, not whatever Google may add later upstream.
- You still need valid Google Analytics access for real account work.

## Helpful docs

- [Browse all Google Analytics docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
