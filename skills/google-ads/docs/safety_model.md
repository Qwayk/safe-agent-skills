# Safety model

Rules:
- This tool supports **reads + writes** to the Google Ads API, but is **plan-first** and safe-by-default.
- Refuse when unsure; do not guess.
- Never log secrets.

## Practical safety notes

- All RPC write methods are dry-run by default: they emit a deterministic plan object unless `--apply` is provided.
- RPC write plans/receipts are safe-by-default: they omit raw request/response payloads (which may contain sensitive data) unless explicitly enabled with `--include-rpc-payload --ack-sensitive-payload`.
- Applying any external write requires explicit gating:
  - `--apply` (opt-in to external mutation)
  - customer-id allowlist (default deny; see `docs/configuration.md`)
  - global kill switch (`GOOGLE_ADS_EXTERNAL_WRITES_DISABLED=1`)
  - before-state capture for supported update operations and readable `CampaignCriterion` ad-schedule removes
  - hard caps on operations per request/run
  - `--yes` for risky/batch operations
  - `--ack-spend` for budget/billing/spend-impacting operations
  - `--ack-irreversible` for remove operations
  - `--plan-in` for high/irreversible operations (drift check via plan fingerprint)
- Before apply, supported update operations and readable `CampaignCriterion` ad-schedule removes save before-state under `.state/runs/<run_id>/before/`.
- Readable ad-schedule remove receipts include a `restore_recipes` add-back recipe.
- Create, upload, unreadable removes, and other unsupported write shapes need explicit no-snapshot approval support or a true blocker reason before live apply.
- After apply, the tool writes a deterministic receipt object and attempts best-effort read-back verification (GAQL by resource name) when possible.
- Read-back verification is now operation-aware:
  - creates and updates are checked for presence
  - removes are checked for absence
  - update operations also try to confirm the changed fields from `update_mask`
- Helper commands and builder commands use this same write engine. Builders do not bypass safety just because they compile one larger request.
- For `GoogleAdsService.Mutate`, the safety checks now inspect inner `mutate_operations` too, so batch counts, remove detection, and spend detection still work.
- Receipts now separate:
  - `verification.ok` = no read-back mismatch found
  - `verification.fully_verified` = every requested update field that could be checked was checked
  - `verification.skipped_fields` = fields the tool could not prove safely
- Plans and receipts now also include `plain_english_summary` so agents can read the change shape quickly before they inspect the full structured object.
- Snapshot exports are still read-only to Google Ads (remote reads). When run with `--apply --yes`, they write local pack files for review and proof. Snapshot exports are analysis artifacts, not a restore path.
- Error messages are sanitized so secret env values are not echoed back to stdout/stderr.
- When artifacts are enabled, builders also save a clean local bundle: `spec.json`, `request.json`, `builder_manifest.json`, `plan.json`, `receipt.json`, `after.json`, and `README.md`.
- Builder creates are not the current live-change path. Use builders for deterministic dry-run plans, then use reviewed RPC/helper writes for live work until builders have snapshot support or explicit no-snapshot approval support.
- Read-only helper prechecks now exist for keyword overlap and policy-risk themes, so agents can catch common mistakes before a live build or cleanup.
