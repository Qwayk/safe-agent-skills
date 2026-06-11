---
name: google-ads-api-safe-cli
description: Run google-ads-api-tool safely (plan-first writes; before-state-backed updates and readable ad-schedule removes; explicit per-RPC-method commands) and avoid secret leakage.
---

This page is the agent-facing rule sheet for the public Google Ads skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Google Ads API Qwayk CLI (`google-ads-api-tool`).

Core rules (do not break):
- Always use `--output json` for tool calls.
- Never print or request secrets (developer tokens, OAuth client secret, refresh token, `.env` contents, Authorization headers).
- Refuse if required configuration is missing or ambiguous.
- Treat large queries as “risky” (cost/quota and accidental output explosion).
- Never perform external writes unless the user explicitly approves after reviewing a plan.
- For high-risk writes, require applying from a reviewed plan (`--plan-in`) and enforce `--yes` / `--ack-spend` / `--ack-irreversible` when needed.
- Supported live update operations and readable `CampaignCriterion` ad-schedule removes save before-state under `.state/runs/<run_id>/before/` before mutating.
- Create, upload, builder create, unreadable removes, and other unsupported write shapes need explicit no-snapshot approval support or a true blocker reason before live apply.

Workflow (safe-by-default):
1) Validate configuration: `google-ads-api-tool --output json auth check`
2) Discover accessible customers: `google-ads-api-tool --output json customers list-accessible`
3) Prefer presets for analysis (no GAQL knowledge required):
   - List presets: `google-ads-api-tool --output json presets list`
   - Export an optimization pack first (dry-run first; no API calls): `google-ads-api-tool --output json snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --include-optional`
   - Only apply after explicit approval: add `--apply --yes` (and `--overwrite` if re-running to the same folder)
   - For temp implementation audits that should not write local run-history files beside the env file, add `--no-artifacts`
   - For deeper analysis, include optional groups: add `--include-optional`
   - Generate the default offline diagnosis from the exported pack: `google-ads-api-tool --output json snapshot analyze diagnose --pack-dir ./out/google-ads-pack`
   - Reuse the exact `recommended_doc_queries` from diagnose before paraphrasing mechanics questions
   - Inspect only the tables tied to the active findings before widening the audit
   - For maximal diagnosis (placements, landing pages, time/network, conversion actions), use `--preset analysis_pack_max_v1` with `--include-optional` only if `optimization_pack_v1` is missing needed tables
   - Keep `snapshot analyze optimize` as the legacy best-effort report, not the default optimization workflow
4) Use explicit RPC method commands for advanced tasks:
   - Command shape: `google-ads-api-tool --output json <service-kebab> <method-kebab> --in request.json`
   - For write methods: run once without `--apply` to get a plan; ask the user to approve only if the request is supported and clear; then run with `--apply` and the required safety flags.
   - Readable `CampaignCriterion` ad-schedule removes are supported when they save before-state and the user approves the irreversible plan.
4b) For repeated account edits, prefer helper commands before hand-writing RPC JSON:
   - `helpers keywords pause-from-list`
   - `helpers keywords add-from-list`
   - `helpers campaign-negatives add-from-list`
   - `helpers campaign set-budget`
   - `helpers campaign set-max-clicks-cpc-ceiling`
   - `helpers entities lookup-by-name`
   - `helpers entities pause` / `helpers entities enable`
   - `helpers campaign-tree pause` / `helpers campaign-tree enable`
   - `helpers precheck overlap`
   - `helpers precheck policy-risk`
   - `helpers offline upload-click-conversions`
4c) For whole campaign creation, prefer strict builders before hand-writing many separate RPC payloads:
   - `builders search-campaign from-spec`
   - `builders competitor-search from-spec`
   - `builders dsa-feed-search from-spec`
   - Use the example spec files in `docs/examples/inputs/` as the starting shape.
5) Use GAQL only for edge cases:
   - Start with `--limit 1` or `--limit 5`.
   - Prefer narrow SELECT fields instead of `SELECT *`.
6) If the user asks for a large export:
   - Start with a short date range first.
   - Use `--max-rows N` to cap rows per group and avoid output explosions.

References:
- Agent skill prompt and install notes are included with this package.
- Docs: `docs/quickstart.md`, `docs/command_reference.md`, `docs/safety_model.md`

Notes:
- Write RPCs are plan-first: without `--apply`, the tool emits a deterministic plan object and does not mutate Google Ads.
- Builder commands are also plan-first. They compile one deterministic `GoogleAdsService.Mutate` request and still use the same spend, batch, and remove safety gates, but create-heavy builder applies are not the current live-change path.
- After supported apply, confirm `before_state.saved` exists before discussing verification.
- For readable ad-schedule removes, read `restore_recipes` before discussing add-back steps.
- After apply, check both `verification.ok` and `verification.fully_verified`. If `fully_verified=false`, read `verification.skipped_fields`.
- For faster review, read `plain_english_summary` first, then inspect the structured plan or receipt.
- Recommendations from `snapshot analyze diagnose` are review-only. The skill must never auto-apply them.
- If `snapshot analyze diagnose` returns `support_route = books_or_human`, do not force the official docs lane to answer the judgment question.
- Do not start a normal optimization audit with `analysis_pack_max_v1`, GAQL, raw table slicing, or ad hoc `jq` summaries.
- Do not paraphrase a diagnose mechanics query before the first exact `recommended_doc_queries` attempt.
