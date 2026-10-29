# Safety model

Google Ads can touch customer access, GAQL reads, campaign settings, budgets, criteria, and bulk mutate work, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the customer and campaign state first, then review the exact plan before anything that can affect spend, targeting, or delivery."

## Core safety rules

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
- Campaign before-state and read-back queries include drafts and still select the exact resource name. Experiment drafts can be updated with the same snapshot protection as ordinary campaigns; missing targets still refuse before mutation.
- Readable ad-schedule remove receipts include a `restore_recipes` add-back recipe.
- Create, upload, unreadable removes, and other unsupported snapshot shapes require explicit `--ack-no-snapshot` approval before apply.
- After apply, the tool writes a deterministic receipt object and attempts best-effort read-back verification (GAQL by resource name) when possible.
- Long-running SDK responses are serialized from their returned operation handle without polling or resubmitting. A receipt for an asynchronous request proves submission only; check the operation and destination state before claiming completion.
- Read-back verification is now operation-aware:
  - creates and updates are checked for presence; presence alone is partial verification
  - keyword creates compare text, match type, positive/negative state, ad group and any requested status, pairing each input with its ordered mutation result
  - removes are checked for absence
  - update operations also try to confirm the changed fields from `update_mask`
  - unsupported create fields, missing results or unreadable requested fields remain partial; a mismatch fails verification
- Helper commands and builder commands use this same write engine. Builders do not bypass safety just because they compile one larger request.
- For `GoogleAdsService.Mutate`, the safety checks now inspect inner `mutate_operations` too, so batch counts, remove detection, and spend detection still work.
- Receipts now separate:
  - `verification.ok` = no read-back mismatch found
  - `verification.fully_verified` = all targets and requested fields were checked, with no mismatches or skipped checks; remove-only requests may be verified by absence
  - `verification.skipped_fields` = fields the tool could not prove safely
- Plans and receipts now also include `plain_english_summary` so agents can read the change shape quickly before they inspect the full structured object.
- Snapshot exports are still read-only to Google Ads (remote reads). When run with `--apply --yes`, they write local pack files for review and proof. Snapshot exports are analysis artifacts, not a restore path.
- Error messages are sanitized so secret env values are not echoed back to stdout/stderr.
- When artifacts are enabled, builders also save a clean local bundle: `spec.json`, `request.json`, `builder_manifest.json`, `plan.json`, `receipt.json`, `after.json`, and `README.md`.
- Builder creates use the same write engine and require explicit no-snapshot approval; live creation has not been verified.
- Read-only helper prechecks now exist for keyword overlap and policy-risk themes, so agents can catch common mistakes before a live build or cleanup.

## Write outcomes and current access

Writes are submitted once, with SDK retries disabled. Reads retain bounded retries. A transport timeout or server error returns `outcome_unknown` and exit status 1, with read-back where possible. Do not replay the request automatically; inspect destination state first.

Partial failures return `partial_failure` and exit status 1. Receipts expose error codes and failed input locations, omitting provider messages/triggers that may echo private data. Reconcile successful items before retrying only failed items. Unknown or malformed detail formats preserve the receipt and increment `partial_failure.undecoded_details`; `errors_decoded` is false if any detail was not understood. Known errors in the same response remain available.

A read-back mismatch returns `verification_failed` and exit status 1. `accepted_unverified` means Google returned a response but completion was not fully proved; `validated` means validation only. Empty read-back targets never count as fully verified. Check the receipt outcome before claiming success.

OAuth credentials and Google Cloud project API access are required; developer tokens are no longer sent. Campaign settings in optimization and maximal-analysis exports include ACA and broad-match AI Max migration dates when Google returns them.
