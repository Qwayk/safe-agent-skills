# instantly-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first CLI for the **Instantly API v2** (Qwayk style): dry-run by default, explicit apply gates for writes, before-state capture for supported live writes, and a plan/receipt workflow for agent review.

This tool does not offer machine rollback or restore today. Supported live writes save the previous API response under `.state/runs/<run_id>/before/` before applying. Unsupported live writes refuse until a safe pre-read is added.

Supported command families (high level):
- Workspace: `whoami`, `health`
- Workspace admin: `workspace get-current|patch-current|create|change-owner|whitelabel-domain ...` (`create` is requires explicit no-snapshot approval when no saved snapshot is available)
- Accounts: `accounts list|get|create|patch|delete|warmup-enable|warmup-disable|pause|resume|mark-fixed|move|test-vitals|ctd-status` (note: `list|get|ctd-status` are sensitive reads; require `--apply --yes` and write response to a receipt file only)
- Workspace billing: `workspace-billing plan-details|subscription-details`
- Workspace members: `workspace-members list|get|create|patch|delete`
- Workspace group members: `workspace-group-members list|admin|get|create|delete`
- OAuth: `oauth google-init|microsoft-init|session-status`
- API keys: `api-keys list|create|delete` (**secret-safe**: raw key material is stored locally under `.state/` only)
- DFY email account orders: `dfy-email-account-orders list-orders|list-accounts|create-order|cancel-accounts|check-domains|similar-domains|prewarmed-domains`
- CRM actions: `crm-actions list-phone-numbers|delete-phone-number`
- Campaigns: `campaigns list|get|create|patch|delete|activate|pause|sending-status|search-by-contact|count-launched|share|create-from-export|export|duplicate|add-variables` (`create`, `create-from-export`, and `duplicate` are requires explicit no-snapshot approval when no saved snapshot is available)
- Subsequences: `subsequences list|get|create|patch|delete|sending-status|pause|resume|duplicate`
- Analytics: `analytics warmup|accounts-daily|account-vitals|campaigns|campaigns-overview|campaigns-daily|campaign-steps`
- Leads: `leads list|get|create|patch|add-bulk|update-interest-status|remove-from-subsequence|bulk-assign|move|move-to-subsequence|delete|bulk-delete|merge` (note: `create` and `add-bulk` are requires explicit no-snapshot approval when no saved snapshot is available; many lead ops are high-risk and require `--apply --yes`; destructive actions require a plan-file workflow)
- Lead organization:
  - `lead-lists list|get|create|patch|delete` (`create` is requires explicit no-snapshot approval when no saved snapshot is available)
  - `lead-labels list|get|create|patch|delete` (`create` is requires explicit no-snapshot approval when no saved snapshot is available)
  - `custom-tags list|get|create|patch|delete|toggle-resource` (`create` and `toggle-resource` are requires explicit no-snapshot approval when no saved snapshot is available)
  - `custom-tag-mappings list`
- Mappings: `account-campaign-mappings get`
- Webhooks: `webhooks list|get|event-types|create|patch|delete|test|resume`, `webhook-events list|get|summary|summary-by-date` (`create` and `test` are requires explicit no-snapshot approval when no saved snapshot is available)
- Inbox placement: `inbox-placement tests|analytics|reports` (`tests create` is requires explicit no-snapshot approval when no saved snapshot is available)
- Email verification: `email-verification status|create` (`create` is requires explicit no-snapshot approval when no saved snapshot is available)
- Audit log: `audit-log list` (raw items hidden by default; use `--include-items --out <path>` for file-only raw output)
- Emails: `emails list|get|unread-count|patch|forward|delete` (`forward` is requires explicit no-snapshot approval when no saved snapshot is available; delete is destructive + plan-in gated)
- Threads: `threads mark-as-read|reply` (live apply requires explicit no-snapshot approval when no saved snapshot is available)
- Do-not-contact: `do-not-contact list|get|create|patch|delete` (`create` is requires explicit no-snapshot approval when no saved snapshot is available)
- Supersearch enrichment: `supersearch-enrichment get|history|create|patch-settings|run|enrich-leads|ai|count-leads|preview-leads` (`patch-settings` can apply with before-state; `create`, `run`, `enrich-leads`, and `ai` are requires explicit no-snapshot approval when no saved snapshot is available)
- Background jobs: `background-jobs list|get`

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Agent skill prompt and install notes are included with this package.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
instantly-api-tool --output json --version
instantly-api-tool --output json onboarding
instantly-api-tool --output json auth check

# Dry-run plan for a write:
instantly-api-tool --output json campaigns create --file examples/campaign_create.json

# Apply a supported write (saves before-state when possible; some commands require --yes):
instantly-api-tool --output json --apply campaigns activate --campaign-id CAMPAIGN_ID

# Irreversible reply workflow (plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available):
instantly-api-tool --output json threads reply --thread-id THREAD_ID --reply-to-uuid REPLY_TO_UUID --message \"Hi!\"  # dry-run plan
instantly-api-tool --output json --plan-out plan.json threads reply --thread-id THREAD_ID --reply-to-uuid REPLY_TO_UUID --message \"Hi!\"  # write plan.json
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`
