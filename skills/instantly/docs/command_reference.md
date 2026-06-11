# Command reference

Use this page when you need the exact Instantly command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags (most used)

- `--output json|text` (default: `json`)
- `--env-file .env` (default: `.env`)
- `--verbose` (HTTP start/end lines to stderr; never prints Authorization headers)
- `--apply` (apply writes and sensitive reads; default is dry-run plan)
- `--yes` (required for high-risk/batch writes)
- `--ack-irreversible` (required for irreversible writes like `threads reply`)
- `--plan-out <file>` / `--plan-in <file>` (write/read plans; `--plan-in` requires `--apply`)
- `--receipt-out <file>` (write receipt on apply)

Plan-first workflow:
- Dry-run writes a plan (and also writes `.state/runs/<run_id>/plan.json` for write-capable commands).
- Delete and irreversible apply require `--plan-in`.
- Supported live writes save before-state under `.state/runs/<run_id>/before/` before applying.
- When a write family cannot save a useful before-state, live apply requires explicit no-snapshot approval before HTTP.
- This tool has no machine rollback or restore path, so the plan/receipt stays honest: `rollback.supported` is `false`, and `rollback_plan` stays `null`.

## Onboarding

- `instantly-api-tool onboarding [--no-write-env]`

## Auth

- `instantly-api-tool --output json --version`
- `instantly-api-tool --output json auth check`

## Workspace

- `instantly-api-tool whoami`
- `instantly-api-tool health`
- `instantly-api-tool workspace get-current`

Update current workspace (apply requires a reviewed plan via `--plan-in`):
- `instantly-api-tool workspace patch-current --file workspace_patch.json`
- `instantly-api-tool --apply --plan-in plan.json workspace patch-current`

Create a workspace (plan-first; live apply requires explicit no-snapshot approval when no useful before-state can be saved):
- `instantly-api-tool workspace create --file workspace_create.json`

Change workspace owner (apply requires a reviewed plan via `--plan-in`):
- `instantly-api-tool workspace change-owner --file change_owner.json`
- `instantly-api-tool --apply --plan-in plan.json workspace change-owner`

Whitelabel domain:
- `instantly-api-tool workspace whitelabel-domain get`
- `instantly-api-tool workspace whitelabel-domain set --file whitelabel_domain.json`
- `instantly-api-tool --apply workspace whitelabel-domain set --file whitelabel_domain.json`
- `instantly-api-tool workspace whitelabel-domain delete`
- `instantly-api-tool --apply --yes --plan-in plan.json workspace whitelabel-domain delete`

## Workspace billing

- `instantly-api-tool workspace-billing plan-details`
- `instantly-api-tool workspace-billing subscription-details`

## Workspace members

- `instantly-api-tool workspace-members list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool workspace-members get --id MEMBER_ID`
- `instantly-api-tool workspace-members create --file workspace_member_create.json`
- Live apply for `workspace-members create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool workspace-members patch --id MEMBER_ID --file workspace_member_patch.json`
- `instantly-api-tool --apply workspace-members patch --id MEMBER_ID --file workspace_member_patch.json`
- `instantly-api-tool workspace-members delete --id MEMBER_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json workspace-members delete`

## Workspace group members

- `instantly-api-tool workspace-group-members list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool workspace-group-members admin`
- `instantly-api-tool workspace-group-members get --id GROUP_MEMBER_ID`
- `instantly-api-tool workspace-group-members create --file workspace_group_member_create.json`
- Live apply for `workspace-group-members create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool workspace-group-members delete --id GROUP_MEMBER_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json workspace-group-members delete`

## OAuth

- `instantly-api-tool oauth google-init --file oauth_google_init.json`
- `instantly-api-tool oauth microsoft-init --file oauth_microsoft_init.json`
- `instantly-api-tool oauth session-status --session-id SESSION_ID`
- OAuth init live apply requires explicit no-snapshot approval when no useful before-state can be saved.

## API keys (secret-safe)

List:
- `instantly-api-tool api-keys list [--limit N] [--starting-after CURSOR]`

Create (secret-bearing; raw key is stored locally under `.state/sensitive/`):
- `instantly-api-tool api-keys create --file api_key_create.json`
- `instantly-api-tool --apply --yes --plan-in plan.json api-keys create --ack-store-secret-locally`

Delete:
- `instantly-api-tool api-keys delete --id API_KEY_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json api-keys delete`

## DFY email account orders

- `instantly-api-tool dfy-email-account-orders list-orders [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool dfy-email-account-orders list-accounts [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool dfy-email-account-orders list-accounts --with-passwords --ack-store-secret-locally`
- `instantly-api-tool dfy-email-account-orders create-order --file dfy_create_order.json`
- `instantly-api-tool dfy-email-account-orders cancel-accounts --file dfy_cancel_accounts.json`
- Live apply for create/cancel requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool dfy-email-account-orders check-domains --file dfy_check_domains.json`
- `instantly-api-tool --apply dfy-email-account-orders check-domains --file dfy_check_domains.json`
- `instantly-api-tool dfy-email-account-orders similar-domains --file dfy_similar_domains.json`
- `instantly-api-tool --apply dfy-email-account-orders similar-domains --file dfy_similar_domains.json`
- `instantly-api-tool dfy-email-account-orders prewarmed-domains`

## CRM actions

- `instantly-api-tool crm-actions list-phone-numbers`
- `instantly-api-tool crm-actions delete-phone-number --id PHONE_NUMBER_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json crm-actions delete-phone-number`

## Campaigns

- `instantly-api-tool campaigns list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool campaigns get --campaign-id CAMPAIGN_ID`
- `instantly-api-tool campaigns create --file examples/campaign_create.json`
- Live apply for `campaigns create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool campaigns activate --campaign-id CAMPAIGN_ID`
- `instantly-api-tool --apply campaigns activate --campaign-id CAMPAIGN_ID`
- `instantly-api-tool campaigns pause --campaign-id CAMPAIGN_ID`
- `instantly-api-tool --apply campaigns pause --campaign-id CAMPAIGN_ID`
- `instantly-api-tool campaigns patch --campaign-id CAMPAIGN_ID --file campaign_patch.json`
- `instantly-api-tool --apply campaigns patch --campaign-id CAMPAIGN_ID --file campaign_patch.json`

Delete (plan-file workflow):
- `instantly-api-tool campaigns delete --campaign-id CAMPAIGN_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json campaigns delete`

Additional endpoints:
- `instantly-api-tool campaigns sending-status --campaign-id CAMPAIGN_ID [--with-ai-summary]`
- `instantly-api-tool campaigns search-by-contact --email user@example.com [--sort-column COL] [--sort-order asc|desc]`
- `instantly-api-tool campaigns count-launched`
- `instantly-api-tool campaigns share --campaign-id CAMPAIGN_ID`
- `instantly-api-tool --apply --yes campaigns share --campaign-id CAMPAIGN_ID`
- `instantly-api-tool campaigns create-from-export --campaign-id CAMPAIGN_ID`
- Live apply for `campaigns create-from-export` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool campaigns export --campaign-id CAMPAIGN_ID`
- `instantly-api-tool --apply campaigns export --campaign-id CAMPAIGN_ID`
- `instantly-api-tool campaigns duplicate --campaign-id CAMPAIGN_ID --file campaign_duplicate.json`
- Live apply for `campaigns duplicate` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool campaigns add-variables --campaign-id CAMPAIGN_ID --file campaign_variables.json`
- `instantly-api-tool --apply campaigns add-variables --campaign-id CAMPAIGN_ID --file campaign_variables.json`

## Accounts

Sensitive reads (credential-bearing responses; file-only output):
- `instantly-api-tool accounts list [--limit N] [--starting-after CURSOR]` (dry-run plan only; no API call)
- `instantly-api-tool --apply --yes accounts list [--limit N] [--starting-after CURSOR]` (writes redacted response to receipt file; stdout includes path only)
- `instantly-api-tool accounts get --email user@example.com` (dry-run plan only; no API call)
- `instantly-api-tool --apply --yes accounts get --email user@example.com` (writes redacted response to receipt file; stdout includes path only)
- `instantly-api-tool accounts create --file account_create.json`
- Live apply for `accounts create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool accounts patch --email user@example.com --file account_patch.json`
- `instantly-api-tool --apply accounts patch --email user@example.com --file account_patch.json`

Delete (plan-file workflow):
- `instantly-api-tool accounts delete --email user@example.com`
- `instantly-api-tool --apply --yes --plan-in plan.json accounts delete`

Warmup (batch):
- `instantly-api-tool accounts warmup-enable --file warmup_enable.json`
- `instantly-api-tool --apply --yes accounts warmup-enable --file warmup_enable.json`
- `instantly-api-tool accounts warmup-disable --file warmup_disable.json`
- `instantly-api-tool --apply --yes accounts warmup-disable --file warmup_disable.json`

Pause/resume:
- `instantly-api-tool accounts pause --email user@example.com`
- `instantly-api-tool --apply accounts pause --email user@example.com`
- `instantly-api-tool accounts resume --email user@example.com`
- `instantly-api-tool --apply accounts resume --email user@example.com`
- `instantly-api-tool accounts mark-fixed --email user@example.com`
- `instantly-api-tool --apply accounts mark-fixed --email user@example.com`

Move (batch):
- `instantly-api-tool accounts move --file move_accounts.json`
- `instantly-api-tool --apply --yes accounts move --file move_accounts.json`

Vitals/status:
- `instantly-api-tool accounts test-vitals --file vitals.json`
- `instantly-api-tool --apply accounts test-vitals --file vitals.json`
- `instantly-api-tool accounts ctd-status` (dry-run plan only; no API call)
- `instantly-api-tool --apply --yes accounts ctd-status` (writes redacted response to receipt file; stdout includes path only)

## Leads

- `instantly-api-tool leads list [--campaign-id CAMPAIGN_ID] [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool leads get --lead-id LEAD_ID`
- `instantly-api-tool leads create --file lead_create.json`
- Live apply for `leads create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool leads patch --lead-id LEAD_ID --file lead_patch.json`
- `instantly-api-tool --apply leads patch --lead-id LEAD_ID --file lead_patch.json`
- `instantly-api-tool leads add-bulk --campaign-id CAMPAIGN_ID --csv examples/leads.csv`
- `instantly-api-tool leads add-bulk --campaign-id CAMPAIGN_ID --json examples/leads.json`
- Live apply for `leads add-bulk` requires explicit no-snapshot approval when no useful before-state can be saved.

High-risk lead operations:
- `instantly-api-tool leads update-interest-status --file update_interest_status.json`
- `instantly-api-tool --apply --yes leads update-interest-status --file update_interest_status.json`
- `instantly-api-tool leads remove-from-subsequence --file remove_from_subsequence.json`
- `instantly-api-tool --apply --yes leads remove-from-subsequence --file remove_from_subsequence.json`
- `instantly-api-tool leads bulk-assign --file bulk_assign.json`
- `instantly-api-tool --apply --yes leads bulk-assign --file bulk_assign.json`
- `instantly-api-tool leads move --file move_leads.json`
- `instantly-api-tool --apply --yes leads move --file move_leads.json`
- `instantly-api-tool leads move-to-subsequence --file move_to_subsequence.json`
- `instantly-api-tool --apply --yes leads move-to-subsequence --file move_to_subsequence.json`

Destructive (plan-file workflow):
- `instantly-api-tool leads delete --lead-id LEAD_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json leads delete`
- `instantly-api-tool leads bulk-delete --file bulk_delete.json`
- `instantly-api-tool --apply --yes --plan-in plan.json leads bulk-delete`
- `instantly-api-tool leads merge --file merge_leads.json`
- `instantly-api-tool --apply --yes --plan-in plan.json leads merge`

## Supersearch enrichment

Advanced feature set (apply requires `--yes`):
- `instantly-api-tool supersearch-enrichment create --file enrichment_create.json`
- Live apply for `supersearch-enrichment create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool supersearch-enrichment patch-settings --resource-id RESOURCE_ID --file enrichment_settings_patch.json`
- `instantly-api-tool --apply --yes supersearch-enrichment patch-settings --resource-id RESOURCE_ID --file enrichment_settings_patch.json`
- `instantly-api-tool supersearch-enrichment run --file enrichment_run.json`
- `instantly-api-tool supersearch-enrichment enrich-leads --file enrich_leads.json`
- `instantly-api-tool supersearch-enrichment ai --file ai_enrichment.json`
- Live apply for `run`, `enrich-leads`, and `ai` requires explicit no-snapshot approval when no useful before-state can be saved.

Read-only:
- `instantly-api-tool supersearch-enrichment get --resource-id RESOURCE_ID`
- `instantly-api-tool supersearch-enrichment history --resource-id RESOURCE_ID`
- `instantly-api-tool supersearch-enrichment count-leads --file count_leads.json`
- `instantly-api-tool supersearch-enrichment preview-leads --file preview_leads.json`

## Lead lists

- `instantly-api-tool lead-lists list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool lead-lists get --lead-list-id LEAD_LIST_ID`
- `instantly-api-tool lead-lists verification-stats --lead-list-id LEAD_LIST_ID`
- `instantly-api-tool lead-lists create --file lead_list_create.json`
- Live apply for `lead-lists create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool lead-lists patch --lead-list-id LEAD_LIST_ID --file lead_list_patch.json`
- `instantly-api-tool --apply lead-lists patch --lead-list-id LEAD_LIST_ID --file lead_list_patch.json`

Delete (plan-file workflow):
- `instantly-api-tool lead-lists delete --lead-list-id LEAD_LIST_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json lead-lists delete`

## Lead labels

- `instantly-api-tool lead-labels list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool lead-labels get --lead-label-id LEAD_LABEL_ID`
- `instantly-api-tool lead-labels create --file lead_label_create.json`
- Live apply for `lead-labels create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool lead-labels patch --lead-label-id LEAD_LABEL_ID --file lead_label_patch.json`
- `instantly-api-tool --apply lead-labels patch --lead-label-id LEAD_LABEL_ID --file lead_label_patch.json`

Delete (plan-file workflow):
- `instantly-api-tool lead-labels delete --lead-label-id LEAD_LABEL_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json lead-labels delete`

## Custom tags

- `instantly-api-tool custom-tags list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool custom-tags get --tag-id TAG_ID`
- `instantly-api-tool custom-tags create --file custom_tag_create.json`
- Live apply for `custom-tags create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool custom-tags patch --tag-id TAG_ID --file custom_tag_patch.json`
- `instantly-api-tool --apply custom-tags patch --tag-id TAG_ID --file custom_tag_patch.json`

Delete (plan-file workflow):
- `instantly-api-tool custom-tags delete --tag-id TAG_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json custom-tags delete`

Toggle mapping (high-risk):
- `instantly-api-tool custom-tags toggle-resource --file tag_mapping_toggle.json`
- Live apply for `custom-tags toggle-resource` requires explicit no-snapshot approval when no useful before-state can be saved.

## Custom tag mappings

- `instantly-api-tool custom-tag-mappings list [--limit N] [--starting-after CURSOR]`

## Account↔campaign mappings

- `instantly-api-tool account-campaign-mappings get --email user@example.com`

## Subsequences

- `instantly-api-tool subsequences list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool subsequences get --subsequence-id SUBSEQUENCE_ID`
- `instantly-api-tool subsequences create --file subsequence_create.json`
- Live apply for `subsequences create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool subsequences patch --subsequence-id SUBSEQUENCE_ID --file subsequence_patch.json`
- `instantly-api-tool --apply subsequences patch --subsequence-id SUBSEQUENCE_ID --file subsequence_patch.json`
- `instantly-api-tool subsequences sending-status --subsequence-id SUBSEQUENCE_ID [--with-ai-summary]`
- `instantly-api-tool subsequences pause --subsequence-id SUBSEQUENCE_ID`
- `instantly-api-tool --apply subsequences pause --subsequence-id SUBSEQUENCE_ID`
- `instantly-api-tool subsequences resume --subsequence-id SUBSEQUENCE_ID`
- `instantly-api-tool --apply subsequences resume --subsequence-id SUBSEQUENCE_ID`
- `instantly-api-tool subsequences duplicate --subsequence-id SUBSEQUENCE_ID`
- Live apply for `subsequences duplicate` requires explicit no-snapshot approval when no useful before-state can be saved.

Delete (plan-file workflow):
- `instantly-api-tool subsequences delete --subsequence-id SUBSEQUENCE_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json subsequences delete`

## Webhooks

- `instantly-api-tool webhooks list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool webhooks get --webhook-id WEBHOOK_ID`
- `instantly-api-tool webhooks event-types`
- `instantly-api-tool webhooks create --file examples/webhook_create.json`
- Live apply for `webhooks create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool webhooks patch --webhook-id WEBHOOK_ID --file webhook_patch.json`
- `instantly-api-tool --apply webhooks patch --webhook-id WEBHOOK_ID --file webhook_patch.json`
- `instantly-api-tool webhooks test --webhook-id WEBHOOK_ID`
- Live apply for `webhooks test` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool webhooks resume --webhook-id WEBHOOK_ID`
- `instantly-api-tool --apply webhooks resume --webhook-id WEBHOOK_ID`
- `instantly-api-tool webhooks delete --webhook-id WEBHOOK_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json webhooks delete --webhook-id WEBHOOK_ID`

## Webhook events

- `instantly-api-tool webhook-events list [--webhook-id WEBHOOK_ID] [--limit N] [--starting-after CURSOR]` (default: `--limit 20`; max: `50`)
- `instantly-api-tool webhook-events get --event-id EVENT_ID`
- `instantly-api-tool webhook-events summary --from 2024-01-01 --to 2024-01-31`
- `instantly-api-tool webhook-events summary-by-date --from 2024-01-01 --to 2024-01-31`

## Emails

- `instantly-api-tool emails list [--limit N] [--starting-after CURSOR]` (default: `--limit 20`)
- `instantly-api-tool emails get --email-id EMAIL_ID`
- `instantly-api-tool emails unread-count`
- `instantly-api-tool emails patch --email-id EMAIL_ID --file email_patch.json`
- `instantly-api-tool --apply emails patch --email-id EMAIL_ID --file email_patch.json`

Irreversible (plan-first; live apply requires explicit no-snapshot approval when no useful before-state can be saved):
- `instantly-api-tool emails forward --file email_forward.json`
- `instantly-api-tool --plan-out plan.json emails forward --file email_forward.json`

Destructive (plan-file workflow):
- `instantly-api-tool emails delete --email-id EMAIL_ID`
- `instantly-api-tool --plan-out plan.json emails delete --email-id EMAIL_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json emails delete`

## Analytics

- `instantly-api-tool analytics warmup --emails user@example.com`
- `instantly-api-tool analytics accounts-daily --emails user@example.com --start-date 2024-01-01 --end-date 2024-01-31`
- `instantly-api-tool analytics account-vitals --emails user@example.com`
- `instantly-api-tool analytics campaigns --start-date 2024-01-01 --end-date 2024-01-31`
- `instantly-api-tool analytics campaigns-overview --start-date 2024-01-01 --end-date 2024-01-31`
- `instantly-api-tool analytics campaigns-daily --campaign-id CAMPAIGN_ID --start-date 2024-01-01 --end-date 2024-01-31`
- `instantly-api-tool analytics campaign-steps --campaign-id CAMPAIGN_ID --start-date 2024-01-01 --end-date 2024-01-31`

## Inbox placement

Tests:
- `instantly-api-tool inbox-placement tests list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool inbox-placement tests get --test-id TEST_ID`
- `instantly-api-tool inbox-placement tests esp-options`
- `instantly-api-tool inbox-placement tests create --file FILE.json`
- Live apply for `inbox-placement tests create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool inbox-placement tests patch --test-id TEST_ID --file FILE.json`
- `instantly-api-tool --apply --yes inbox-placement tests patch --test-id TEST_ID --file FILE.json`
- `instantly-api-tool inbox-placement tests delete --test-id TEST_ID`
- `instantly-api-tool --apply --yes inbox-placement tests delete --test-id TEST_ID`

Analytics + reports:
- `instantly-api-tool inbox-placement analytics list --test-id TEST_ID [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool inbox-placement analytics get --analytics-id ANALYTICS_ID`
- `instantly-api-tool inbox-placement analytics stats-by-test-id --test-id TEST_ID`
- `instantly-api-tool inbox-placement analytics deliverability-insights --test-id TEST_ID`
- `instantly-api-tool inbox-placement analytics stats-by-date --test-id TEST_ID`
- `instantly-api-tool inbox-placement reports list --test-id TEST_ID [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool inbox-placement reports get --report-id REPORT_ID`

## Email verification

- `instantly-api-tool email-verification status --email user@example.com`
- `instantly-api-tool email-verification create --email user@example.com`
- Live apply for `email-verification create` requires explicit no-snapshot approval when no useful before-state can be saved.

## Audit log

- `instantly-api-tool audit-log list --start-date 2024-01-01 --end-date 2024-01-31 [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool audit-log list --start-date 2024-01-01 --end-date 2024-01-31 --include-items --out audit-logs.json`

## Threads

- `instantly-api-tool threads mark-as-read --thread-id THREAD_ID`
- Live apply for `threads mark-as-read` requires explicit no-snapshot approval when no useful before-state can be saved.

Reply (irreversible; plan-first):
- `instantly-api-tool threads reply --thread-id THREAD_ID --reply-to-uuid REPLY_TO_UUID --message "Hello"`
- Live apply for `threads reply` requires explicit no-snapshot approval when no useful before-state can be saved.

## Do-not-contact

- `instantly-api-tool do-not-contact list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool do-not-contact get --entry-id ENTRY_ID`
- `instantly-api-tool do-not-contact create --email user@example.com`
- Live apply for `do-not-contact create` requires explicit no-snapshot approval when no useful before-state can be saved.
- `instantly-api-tool do-not-contact patch --entry-id ENTRY_ID --file dnc_patch.json`
- `instantly-api-tool --apply --yes do-not-contact patch --entry-id ENTRY_ID --file dnc_patch.json`
- `instantly-api-tool do-not-contact delete --entry-id ENTRY_ID`
- `instantly-api-tool --apply --yes --plan-in plan.json do-not-contact delete --entry-id ENTRY_ID`

## Background jobs

- `instantly-api-tool background-jobs list [--limit N] [--starting-after CURSOR]`
- `instantly-api-tool background-jobs get --job-id JOB_ID`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `instantly-api-tool runs list [--limit 20]`
- `instantly-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`
