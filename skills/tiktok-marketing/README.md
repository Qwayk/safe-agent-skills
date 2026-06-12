# TikTok Marketing

**Capability:** Reads + careful changes

TikTok Marketing is where campaign setup, ad groups, creatives, pixels, catalogs, reports, and advertiser access decide what can run on TikTok for Business.

This skill helps an agent confirm TikTok Marketing access, review advertisers, campaigns, ad groups, ads, creatives, reports, pixels, catalogs, and business-center data, and prepare upload or campaign-change plans before anything writes to TikTok.

Use it for questions like: "Does this advertiser access work?", "What campaigns or ads should we review?", "Can you plan a report request?", "Can you prepare an image or video upload flow?", or "Which pinned operation fits this TikTok job?"

TikTok Marketing work starts best with one credential check and one small advertiser or campaign read. The general `api` surface needs `--live` for real reads, write-like operations stay plan-first, and current writes still need explicit no-snapshot approval when the command cannot save real before-state first. `auth check` is the one special live helper because it validates your TikTok credentials directly.

A good first ask is: "Check the TikTok Marketing connection, tell me whether my access works, and show me what campaign or advertiser reads are safe to review first."

## Start here first

- Want ideas for real TikTok Marketing work? [What you can do with TikTok Marketing](docs/use_cases.md)
- Need setup? [Connect your TikTok Marketing account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review campaigns, ad groups, ads, and advertiser status before anyone changes live delivery.
- Check official operation coverage and inspect the exact pinned command surface.
- Plan campaign, ad, creative, or upload changes before any TikTok write is attempted.
- Run auth and access checks so you can confirm app credentials and advertiser visibility first.
- Save plans, refusal outputs, run history, and proof artifacts for later review.

## What access this skill needs

- `TIKTOK_MARKETING_APP_ID`
- `TIKTOK_MARKETING_APP_SECRET`
- `TIKTOK_MARKETING_ACCESS_TOKEN`, or a local `.state/token.json` token file
- Query or body JSON files for most real `api` operations
- The right advertiser permissions for the operations you want to use

## Install and first run

Install slug: `tiktok-marketing`

Ask your agent to install the `tiktok-marketing` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@tiktok-marketing -g -y
```

Then try a safe first ask like:

```text
Check the TikTok Marketing connection, tell me whether auth works, and help me plan one safe campaign or advertiser read first.
```

## How this skill stays safe

- The broad `api` command surface does not hit TikTok unless you add `--live`.
- `auth check` is a special live helper that validates credentials directly.
- Write-like operations start as dry-run plans first.
- Apply attempts need the normal write gates and still require explicit no-snapshot approval when no real before-state support exists.
- There is no raw request bridge.
- Plans, refusal outputs, run history, docs, tests, and the coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- the pinned official TikTok Marketing operation surface with **240** named `api <operation-command>` commands
- auth helpers like `auth check`, `auth token set`, and `auth token status`
- campaign, ad group, ad, creative, advertiser, report, pixel, catalog, business-center, and other official operation families
- plan-first write behavior for the current write-like operations

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the operation, request files, and target advertiser context.
- `auth check` can run as the first live access test.
- Normal `api` reads need `--live`.
- Write attempts need the full apply path and still need explicit no-snapshot approval when saved before-state is missing.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Runs can save local history under `.state/runs`.
- Refusal outputs prove when a write stopped before provider HTTP.
- The docs, tests, examples, and API coverage ledger all stay in this repo.

## Limits

- The general `api` surface is explicit, but it still depends on the real TikTok permissions and request shapes for each operation.
- Current write-like operations do not have broad saved before-state support.
- Approved writes still need explicit no-snapshot approval when the tool cannot save useful prior state.
- This skill is safest when you start with one auth check and one reviewed plan before larger work.

## Helpful docs

- [Browse all TikTok Marketing docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
