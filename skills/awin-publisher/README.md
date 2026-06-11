# Awin Publisher

**Capability:** Reads + careful changes

Use this skill when you want your agent to work with Awin publisher accounts, programs, offers, transactions, reports, tracking links, feeds, and proof-of-purchase uploads without guessing from raw docs.

You can hand your agent jobs like joined-program checks, offer reviews, transaction follow-up, advertiser or campaign reporting, enhanced or legacy feed downloads, linkbuilder tasks, and proof-of-purchase upload planning.

Most publisher work stays read-only or download-only. The one remote write path, `proof-of-purchase orders create`, starts as a dry-run plan and only goes live after explicit approval with the reviewed plan file. There is no raw request bridge.

A good first ask is: "Check the Awin Publisher skill is configured, show me the most important recent programs and transactions, and stop before any live proof-of-purchase upload."

## Start here first

- Want ideas for real Awin publisher work? [What you can do with Awin Publisher](docs/use_cases.md)
- Need setup? [Connect your Awin publisher account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Confirm that your token can reach the right publisher account before you trust any live report.
- Check joined, pending, suspended, rejected, or hidden programs for a publisher.
- Pull offers, transactions, and transaction queries into a repeatable workflow.
- Review advertiser, campaign, and creative performance with explicit report commands.
- Generate one tracking link or a prepared batch with clear input files.
- Download enhanced or legacy feeds to local files you can inspect later.
- Prepare a proof-of-purchase upload in dry-run mode before anyone sends it live.

## What access this skill needs

- `AWIN_API_TOKEN` for most publisher reads, reports, linkbuilder work, offers, transactions, and enhanced feed downloads.
- `AWIN_FEED_API_KEY` only for legacy feed list and legacy feed download helpers.
- `AWIN_PROOF_OF_PURCHASE_API_KEY` only for proof-of-purchase uploads.
- A `publisher ID` for most live commands, plus an `advertiser ID` when you work with program details, reports, links, feeds, or proof-of-purchase uploads.
- Local file paths for feed downloads and proof-of-purchase order files.

## Install and first run

Install slug: `awin-publisher`

Ask your agent to install the `awin-publisher` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@awin-publisher -g -y
```

Then try a safe first ask like:

```text
Check the Awin Publisher skill is configured, list the publisher accounts this token can use, show me the most useful recent transactions, and stop before any live proof-of-purchase upload.
```

## How this skill stays safe

- Read commands do not change Awin data.
- Feed downloads only write local files when you choose `--out`.
- `proof-of-purchase orders create` starts as a dry-run plan by default.
- Live proof-of-purchase uploads need `--apply --yes --plan-in`.
- `--plan-in` rechecks the reviewed plan against the current environment and the requested publisher and advertiser ids.
- `--receipt-out` can save the final apply receipt.
- There is no raw request bridge.

## What it covers today

This skill covers:

- onboarding and auth checks
- publisher account and program lookup
- offers, transactions, and transaction queries
- advertiser, campaign, and creative reports
- linkbuilder generate, batch generate, and quota
- enhanced and legacy feed downloads
- proof-of-purchase order upload planning and apply

## What happens before live changes

- The agent should show the dry-run plan first for proof-of-purchase uploads.
- You review the publisher ID, advertiser ID, order file, and target environment before apply.
- Read commands can run immediately.
- Feed downloads only write locally when you give an explicit `--out` path.
- Live proof-of-purchase uploads need `--apply --yes --plan-in`.
- After apply, the tool can write a receipt for the final result.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Read commands and write flows can log to JSONL audit files when you ask for them.
- Local run history can keep command, result, and artifact paths under `.state/runs/`.
- The docs, tests, examples, and API coverage ledger all live in this repo.

## Limits

- `proof-of-purchase orders create` is the only remote write command in this tool today.
- Live proof-of-purchase use still needs both Awin-side publisher enablement and advertiser-side CLO enablement.
- Live Awin credential proof is not stored in this repo because no real credentials are committed here.
- Different Awin command families use different auth flows, so the tool keeps those splits explicit instead of pretending one key works everywhere.
- There is no raw request bridge.

## Helpful docs

- [Browse all Awin Publisher docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
