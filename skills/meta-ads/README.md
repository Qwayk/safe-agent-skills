# Meta Ads API tool (read-only)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

This is a safety-first CLI for Meta Ads (Marketing API) reporting and inventory.

Key idea: **GET-only**. This tool refuses non-GET requests and does not implement any remote writes.

## Start here (non-technical)

- Use cases: `docs/use_cases.md`
- Media-buyer quickstart: `docs/media_buyer_quickstart.md`
- Winning ads workbook: `docs/winning_ads_workbook.md`
- Onboarding (how to get a token + account id): `docs/onboarding.md`
- Safety model: `docs/safety_model.md`
- Proof pack (what we verified + examples): `docs/proof.md`

## Quickstart (CLI)

```bash
meta-ads-api-tool --output json --version
meta-ads-api-tool onboarding
meta-ads-api-tool --output json auth check
```

## What you can do (read-only)

- List/get ad accounts, campaigns, ad sets, ads, creatives, images, and videos
- Pull insights at account/campaign/adset/ad level (GET-only)
- Compare two date ranges with identical settings (`insights compare`)
- Export analysis-ready snapshot packs (manifest + JSONL tables) via `snapshot export`
- Opt-in creative asset downloads during snapshot export (`--download-assets`)
- Extract a normalized creative “anatomy” (`creatives anatomy`) and fetch creative previews (`previews get`)
- Discover built-in workflow presets (`presets list/show`)

## Docs index

- Docs home: `docs/README.md`
- Command reference: `docs/command_reference.md`
- Presets reference: `docs/presets_reference.md`
- Snapshot export: `docs/snapshot_export.md`
- Agent recipes: `docs/agent_recipes.md`
- Configuration: `docs/configuration.md`
- API coverage ledger: `docs/api_coverage.md`

## Skills wrapper

If your agent runtime supports “skills”, use:
- Skill: `skills/meta-ads-api-safe-cli/SKILL.md`
- Skill docs: `docs/skills_wrappers.md`
