# Awin Advertiser

**Capability:** Reads + careful changes

Awin Advertiser is where a brand or advertiser checks publisher performance, transactions, campaign reports, offers, product feeds, and conversion orders. This skill helps an agent review the account first, then prepare advertiser-side changes only after a dry-run plan is clear.

It is useful for questions like "Which publishers drove results last month?", "Do these transactions need follow-up?", "Is this batch validation file safe to submit?", or "What should we check before uploading an offer, feed, or conversion order?"

Read work can run after setup. Advertiser-side writes start as dry-run plans, live apply needs the normal review gates, and current writes leave plans and receipts but do not promise a broad saved before-state or automatic restore. There is no raw request bridge.

A good first ask is: "Check the Awin Advertiser skill is configured, show me which publishers drove results recently, and help me plan the safest next advertiser action."

## Start here first

- Want ideas for real Awin advertiser work? [What you can do with Awin Advertiser](docs/use_cases.md)
- Need setup? [Connect your Awin advertiser account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check that an Awin advertiser account is connected before anyone tries a live advertiser change.
- Review publishers, campaigns, and transactions to see what is driving results.
- Look up transaction jobs and known transaction IDs when you need follow-up.
- Dry-run transaction batch validation before any approval, decline, or amend request is sent.
- Prepare offer creation, product-feed uploads, and conversion orders with a review step first.

## What access this skill needs

- `AWIN_API_TOKEN`
- `AWIN_ADVERTISER_ID`
- JSON or JSONL input files for batch validation, offers, feeds, or conversion orders when you do those jobs
- The same `AWIN_API_TOKEN` also covers conversion orders, but that official endpoint uses a different auth style under the hood

## Install and first run

Install slug: `awin-advertiser`

Ask your agent to install the `awin-advertiser` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@awin-advertiser -g -y
```

Then try a safe first ask like:

```text
Check the Awin Advertiser skill is configured, show me which publishers drove results last month, and stop before any live advertiser write.
```

## How this skill stays safe

- Read commands do not change the Awin account.
- Write commands start as dry-run plans by default.
- Live writes need `--apply --yes --ack-irreversible --plan-in`.
- Plans and receipts can be saved with `--plan-out` and `--receipt-out`.
- Current write families leave a review trail, but they do not promise a broad saved before-state or automatic restore path.
- There is no raw request bridge.

## What it covers today

This skill covers:

- auth and advertiser connectivity checks
- publisher lookups
- transaction reads and transaction-job status checks
- publisher and campaign reports
- transaction batch validation
- offer creation
- product-feed uploads
- conversion-order posting

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the advertiser ID, target action, and any input file paths.
- Read commands can run immediately.
- Live writes need `--apply --yes --ack-irreversible --plan-in`.
- After apply, the tool can write a receipt for the final result.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Local run history can capture the command, result, and artifact paths.
- The docs, tests, examples, and API coverage ledger all live in this repo.

## Limits

- No raw request bridge.
- Live Awin advertiser proof is not stored in this repo because no real credentials are committed here.
- Current write families do not provide a broad saved before-state or one-click restore.
- Auth details differ by endpoint family, so the skill keeps those mappings explicit instead of pretending one rule fits every Awin endpoint.

## Helpful docs

- [Browse all Awin advertiser docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
