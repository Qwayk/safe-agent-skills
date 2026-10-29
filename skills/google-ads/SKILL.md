---
name: google-ads-api-safe-cli
description: Run google-ads-api-tool safely (plan-first writes; before-state-backed updates and readable ad-schedule removes; explicit per-RPC-method commands) and avoid secret leakage.
---

This page is the agent-facing rule sheet for the public Google Ads skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Google Ads API Qwayk CLI (`google-ads-api-tool`).

Runtime: tool 0.7.3, Google Ads API v25 with v25.1 definitions, Python client 32.0.0. Do not send v22 requests. The retired CampaignLifecycleGoalService and CustomerLifecycleGoalService commands are unavailable; review payloads against Goal and CampaignGoalConfig before replacing them.

Core rules (do not break):
- Always use `--output json` for tool calls.
- Never print or request secrets (developer tokens, OAuth client secret, refresh token, `.env` contents, Authorization headers).
- Refuse if required configuration is missing or ambiguous.
- Treat large queries as “risky” (cost/quota and accidental output explosion).
- Never perform external writes unless the user explicitly approves after reviewing a plan.
- For high-risk writes, require applying from a reviewed plan (`--plan-in`) and enforce `--yes` / `--ack-spend` / `--ack-irreversible` when needed.
- Supported live update operations and readable `CampaignCriterion` ad-schedule removes save before-state under `.state/runs/<run_id>/before/` before mutating.
- Create, upload, builder create, and unreadable remove requests require explicit `--ack-no-snapshot` approval plus the other write gates.

Workflow (safe-by-default):
1) Validate configuration: `google-ads-api-tool --output json auth check`
2) Discover accessible customers: `google-ads-api-tool --output json customers list-accessible`
3) Read the data needed for the user's question directly:
   - `google-ads-api-tool --output json gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT campaign.id, campaign.name, campaign.status FROM campaign"`
   - Omit `--limit` when complete query results are needed. If `meta.limited` is true, retrieve the missing evidence before making completeness claims. A GAQL LIMIT still restricts the requested dataset.
   - Generic presets, exports and comparisons are optional. Snapshot export is read-only upstream but writes local files with `--apply --yes`; select needed groups and inspect completeness.
   - Legacy `snapshot analyze diagnose` and `optimize` remain available for compatibility; they are heuristic reports, not a required investigation path or verified advertising judgment.
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
5) Select relevant GAQL fields and dates. A small `--limit` is useful for exploring shape, not proving full coverage. `--page-size` is ignored (compatibility only).
6) If the user asks for a large export:
   - Start with a short date range first.
   - Use `--max-rows N` to cap rows per group and avoid output explosions.

References:
- Agent skill prompt and install notes are included with this package.
- Docs: `docs/quickstart.md`, `docs/command_reference.md`, `docs/safety_model.md`

Notes:
- Write RPCs are plan-first: without `--apply`, the tool emits a deterministic plan object and does not mutate Google Ads.
- Builder commands are also plan-first. They compile one deterministic `GoogleAdsService.Mutate` request and still use the same spend, batch, and remove safety gates, and create-heavy applies require explicit no-snapshot approval.
- After supported apply, confirm `before_state.saved` exists before discussing verification.
- For readable ad-schedule removes, read `restore_recipes` before discussing add-back steps.
- After apply, check both `verification.ok` and `verification.fully_verified`. If `fully_verified=false`, read `verification.skipped_fields`.
- For faster review, read `plain_english_summary` first, then inspect the structured plan or receipt.
- Recommendations from `snapshot analyze diagnose` are review-only. The skill must never auto-apply them.

## Write outcomes and current access

Writes are submitted once, with SDK retries disabled. Reads retain bounded retries. A transport timeout or server error returns `outcome_unknown` and exit status 1, with read-back where possible. Do not replay the request automatically; inspect destination state first.

Partial failures return `partial_failure` and exit status 1. Receipts expose error codes and failed input locations, omitting provider messages/triggers that may echo private data. Reconcile successful items before retrying only failed items. Unknown or malformed detail formats preserve the receipt and increment `partial_failure.undecoded_details`; `errors_decoded` is false if any detail was not understood. Known errors in the same response remain available.

A read-back mismatch returns `verification_failed` and exit status 1. `accepted_unverified` means Google returned a response but completion was not fully proved; `validated` means validation only. Empty read-back targets never count as fully verified. Check the receipt outcome before claiming success.

OAuth credentials and Google Cloud project API access are required; developer tokens are no longer sent. Campaign settings in optimization and maximal-analysis exports include ACA and broad-match AI Max migration dates when Google returns them.
