# google-ads-api-tool (Google Ads API)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safe-by-default Google Ads API CLI with full read + write RPC coverage (explicit per-method commands; plan-first writes).
It also now includes a small helper layer for repeated account work like pausing keywords, adding negatives, changing budgets, changing Maximize Clicks bid ceilings, looking up entities by name, toggling whole campaign trees, and uploading click conversions.
For whole campaign builds, it also includes strict builders that compile one safe `GoogleAdsService.Mutate` request from a reviewed spec file.
Supported live update operations and readable `CampaignCriterion` ad-schedule removes now save before-state under `.state/runs/<run_id>/before/` before mutating. Create, upload, unreadable removes, and whole-campaign builder live applies still need explicit no-snapshot approval support or a true blocker reason before live apply.

Default optimization workflow:
- export `optimization_pack_v1`
- run `snapshot analyze diagnose`
- use Google-owned docs support for any high-importance findings
- build a no-apply recommendation before any live mutation

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Media buyer quickstart (no GAQL): `docs/media_buyer_quickstart.md`
- Winning ads workbook (how to use the pack): `docs/winning_ads_workbook.md`
- KPI dictionary (what metrics mean + how to compute KPIs): `docs/kpi_dictionary.md`
- Agent recipes (question → preset → commands → tables): `docs/agent_recipes.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Skills wrappers (required for customer-ready tools): `docs/skills_wrappers.md`

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`
- Presets reference (what each pack exports): `docs/presets_reference.md`
- Snapshot export reference (pack layout contract): `docs/snapshot_export_reference.md`

Dependency note:
- This tool requires the Google Ads Python client (`google-ads`). It is installed automatically when you install the tool.
- If you see a “Google Ads client library is not installed” error, run `python -m pip install google-ads` and retry.

Minimal examples:

```bash
google-ads-api-tool --version
google-ads-api-tool onboarding
google-ads-api-tool presets list
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/pack --apply --yes
# Default offline optimization diagnosis from an exported pack:
google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/pack
# Temp implementation audit path with no client run-history writes:
google-ads-api-tool --no-artifacts snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./tmp/pack --apply --yes --include-optional
# Include optional groups (RSA asset labels, landing pages, placements, device/network/hour context):
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/pack --apply --yes --include-optional
# Legacy best-effort report:
google-ads-api-tool snapshot analyze optimize --pack-dir ./out/pack
```

RPC methods (explicit per-service, per-method commands):

```bash
# Read RPC example (requires credentials):
google-ads-api-tool google-ads-service search --in ./search_request.json

# Write RPC example (dry-run plan by default):
google-ads-api-tool campaign-service mutate-campaigns --in ./mutate_campaigns_request.json

# Helper example: pause existing keyword criteria from a JSON list:
google-ads-api-tool helpers keywords pause-from-list --customer-id YOUR_CUSTOMER_ID --items ./keyword_pause_items.json

# Helper example: set a Maximize Clicks CPC ceiling:
google-ads-api-tool helpers campaign set-max-clicks-cpc-ceiling --customer-id YOUR_CUSTOMER_ID --campaign-id YOUR_CAMPAIGN_ID --amount 15

# Helper example: look up a campaign by name before a change:
google-ads-api-tool helpers entities lookup-by-name --customer-id YOUR_CUSTOMER_ID --resource-type campaign --name "Main Search"

# Helper example: pause one whole campaign tree:
google-ads-api-tool helpers campaign-tree pause --customer-id YOUR_CUSTOMER_ID --campaign-name "Main Search" --include-ad-groups --include-ads

# Helper example: read-only overlap check before a new build:
google-ads-api-tool helpers precheck overlap --customer-id YOUR_CUSTOMER_ID

# Builder example: compile a Search campaign from a strict spec file:
google-ads-api-tool builders search-campaign from-spec --spec ./docs/examples/inputs/builder_search_campaign_spec.json
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

Write receipts now separate 2 ideas:
- `verification.ok=true` means the read-back check did not find a mismatch or failed remove.
- `verification.fully_verified=true` means the tool also checked every update field it safely could. If this is false, read `verification.skipped_fields`.
- plans and receipts now also include `plain_english_summary` so future agents can read the change quickly without parsing the whole receipt first.
- readable ad-schedule remove receipts include `before_state.saved` and a `restore_recipes` add-back recipe.

Whole-campaign builders use the same write gates as normal RPC writes:
- dry-run first unless you pass `--apply`
- budget or other spend-impacting builds still require `--ack-spend`
- high-risk or batch applies still require `--yes`
- builder creates are not the current live-change path; use reviewed RPC/helper writes for live work until builders have snapshot support or explicit no-snapshot approval support
- if artifacts are enabled, the run folder includes `spec.json`, `request.json`, `builder_manifest.json`, `plan.json`, `receipt.json`, `after.json`, and `README.md`
