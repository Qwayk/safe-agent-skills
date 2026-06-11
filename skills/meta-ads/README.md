# Meta Ads

**Capability:** Read-only

Use this skill when you want your agent to review Meta ad accounts, campaigns, ad sets, ads, creatives, previews, and insights without guessing from raw docs.

You can hand your agent jobs like account inventory checks, campaign and ad status reviews, date-range performance pulls, winning-ad analysis, creative anatomy review, and snapshot exports for deeper reporting work.

This skill stays simple on purpose: it is GET-only and read-only. It does not create, pause, update, or delete anything in Meta Ads, so the safe path is to inspect the account clearly and leave any live changes to a different tool or a human.

A good first ask is: "Check the Meta Ads skill is connected, list my ad accounts, show one campaign performance report, and export a small snapshot pack."

## Start here first

- Want ideas for real Meta Ads work? [What you can do with Meta Ads](docs/use_cases.md)
- Need setup? [Connect your Meta Ads account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you want more guided reporting paths after that, use the [Media buyer quickstart](docs/media_buyer_quickstart.md) and the [Winning ads workbook](docs/winning_ads_workbook.md).

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- List ad accounts, campaigns, ad sets, ads, creatives, images, videos, and other read-only Meta Ads inventory.
- Pull insights at account, campaign, ad set, or ad level.
- Compare two date ranges with matching settings to spot fatigue, promotion effects, or creative changes.
- Export analysis-ready snapshot packs with manifests and JSONL tables.
- Download creative assets during snapshot export when you opt in explicitly.
- Inspect creative anatomy and fetch creative previews for ad review work.

## What access this skill needs

- A Meta access token with `ads_read`.
- Your Meta ad account ID for the most useful reporting flows.
- Enough account access in Meta Business Manager or Ads Manager to read the account you want.

## Install and first run

Install slug: `meta-ads`

Ask your agent to install the `meta-ads` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@meta-ads -g -y
```

Then try a safe first ask like:

```text
Check the Meta Ads skill is connected, list my ad accounts, show one campaign performance report, and export a small snapshot pack.
```

## How this skill stays safe

- It is GET-only and read-only by design.
- It refuses non-GET Meta requests and does not implement remote writes.
- Pagination stays deterministic so repeated reads are easier to verify.
- Token redaction stays on for stdout, stderr, and verbose logs.
- Snapshot export downloads creative assets only when you opt in.
- Docs, tests, proof files, and the API coverage ledger all live in this repo.

## What it covers today

This skill covers:

- inventory reads for ad accounts, campaigns, ad sets, ads, creatives, images, and videos
- Meta insights pulls, date-range comparisons, and presets
- snapshot export for analysis-ready reporting packs
- creative anatomy inspection and creative preview fetches

## What happens before a real change

This skill does not change anything in Meta Ads. It reads account data, reports what it found, and can export local reporting files when you ask for them.

## What proof it leaves behind

- JSON output can be saved from the commands you run.
- Snapshot export leaves a manifest plus JSONL tables.
- The proof pack includes redacted example outputs and verified command shapes.
- The docs, tests, and API coverage ledger are all in this repo.

## Limits

- No creates, updates, pauses, deletes, or other remote Meta Ads writes.
- Live reads still depend on a valid token and real Meta account access.
- Some useful ad-review work can still need local interpretation after the raw export is produced.
- This tool only helps with reporting, inventory, and analysis flows.

## Helpful docs

- [Browse all Meta Ads docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Media buyer quickstart](docs/media_buyer_quickstart.md)
- [Winning ads workbook](docs/winning_ads_workbook.md)
- [Snapshot export guide](docs/snapshot_export.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
