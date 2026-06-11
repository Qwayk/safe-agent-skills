# API coverage (endpoints → CLI)

Use this page when you want to check whether an Instantly API area already has a CLI command in this skill, and what safety gates apply to it.

## Summary

- Provider: Instantly.ai
- API base URL (tool default): `https://api.instantly.ai/api/v2`
- Auth method: API key via `Authorization: Bearer <INSTANTLY_API_KEY>`
- Pagination (where supported): request `limit`, `starting_after`; response `next_starting_after` surfaced in CLI JSON output
- Last audited (UTC): 2026-06-04
- Before-state policy: supported live writes save before-state under `.state/runs/<run_id>/before/`; unsupported live writes require explicit no-snapshot approval before HTTP until a safe pre-read exists.

## Group coverage ledger (API v2)

Source: Instantly docs sitemap (`https://developer.instantly.ai/sitemap.xml`) enumerates 33 API v2 groups.

Legend:
- **implemented**: has CLI commands in this tool.
- **not implemented (schemas only)**: the group appears in the docs sitemap and API explorer navigation, but the API explorer does not list any callable operations/paths for it (schemas only), so implementing it would require guessing.

| Group (sitemap) | Coverage | Notes |
|---|---|---|
| `account` | implemented | Accounts CRUD + warmup + pause/resume + vitals + CTD status (sensitive reads are file-only) |
| `accountcampaignmapping` | implemented | Read-only per official docs |
| `analytics` | implemented | Account + campaign analytics endpoints |
| `apikey` | implemented | Secret-safe outputs (file-only) |
| `auditlog` | implemented | Raw items hidden by default; file-only for raw output |
| `backgroundjob` | implemented |  |
| `blocklistentry` | implemented | CLI uses `do-not-contact` naming |
| `campaign` | implemented |  |
| `campaignsubsequence` | implemented | Subsequences CRUD |
| `crmactions` | implemented | Delete is destructive (plan-in required) |
| `customprompttemplate` | not implemented (schemas only) | API explorer shows schemas only (no operations/paths as of 2026-02-22) |
| `customtag` | implemented | CRUD + toggle resource |
| `customtagmapping` | implemented | List only (read-only per official docs) |
| `dfyemailaccountorder` | implemented | `with_passwords` is secret-bearing (file-only) |
| `email` | implemented | Includes threads sub-features |
| `emailtemplate` | not implemented (schemas only) | API explorer shows schemas only (no operations/paths as of 2026-02-22) |
| `emailverification` | implemented | Create (apply-gated) + status |
| `inboxplacementanalytics` | implemented | List/get + stats endpoints |
| `inboxplacementblacklistandspamassassinreport` | implemented | List/get report endpoints |
| `inboxplacementtest` | implemented | Create/patch/delete are apply-gated; create is irreversible-gated |
| `lead` | implemented |  |
| `leadlabel` | implemented | CRUD |
| `leadlist` | implemented | CRUD |
| `oauth` | implemented | OAuth init/status only (no token handling) |
| `salesflow` | not implemented (schemas only) | API explorer shows schemas only (no operations/paths as of 2026-02-22) |
| `schemas` | not implemented (schemas only) | API explorer shows schemas only (no operations/paths as of 2026-02-22) |
| `supersearchenrichment` | implemented |  |
| `webhook` | implemented |  |
| `webhookevent` | implemented |  |
| `workspace` | implemented | `whoami`, `health`, workspace admin updates |
| `workspacebilling` | implemented | read-only |
| `workspacegroupmember` | implemented | Delete is destructive (plan-in required) |
| `workspacemember` | implemented | Delete is destructive (plan-in required) |

## Delta ledger (Phases 5–6)

Every item below is present in the official Instantly API v2 explorer (via the docs sitemap). These were gaps in `v0.4.0` and are addressed in the CLI by `v0.6.0` (Phases 5–6) without guessing fields.

Legend:
- **implemented**: covered by CLI.

| Method | Path | Official doc URL | Proposed CLI command | Classification | Notes |
|---|---|---|---|---|---|
| `POST` | `/accounts/move` | https://developer.instantly.ai/api/v2/account/moveaccounts | `instantly-api-tool accounts move --file ...` | implemented | Batch operation; apply requires `--yes` |
| `POST` | `/accounts/{email}/mark-fixed` | https://developer.instantly.ai/api/v2/account/markaccountfixed | `instantly-api-tool accounts mark-fixed --email ...` | implemented | Write; apply-gated |
| `PATCH` | `/campaigns/{id}` | https://developer.instantly.ai/api/v2/campaign/patchcampaign | `instantly-api-tool campaigns patch --campaign-id ... --file ...` | implemented | Write; apply-gated |
| `DELETE` | `/campaigns/{id}` | https://developer.instantly.ai/api/v2/campaign/deletecampaign | `instantly-api-tool campaigns delete --campaign-id ...` | implemented | Destructive; apply requires `--yes --plan-in` |
| `GET` | `/campaigns/{id}/sending-status` | https://developer.instantly.ai/api/v2/campaign/getcampaignsendingstatus | `instantly-api-tool campaigns sending-status --campaign-id ...` | implemented | Read-only |
| `GET` | `/campaigns/search-by-contact` | https://developer.instantly.ai/api/v2/campaign/searchbycontact | `instantly-api-tool campaigns search-by-contact --email ...` | implemented | Read-only |
| `POST` | `/campaigns/{id}/share` | https://developer.instantly.ai/api/v2/campaign/sharecampaign | `instantly-api-tool campaigns share --campaign-id ...` | implemented | High-impact; apply requires `--yes` |
| `POST` | `/campaigns/{id}/from-export` | https://developer.instantly.ai/api/v2/campaign/createfromexport | `instantly-api-tool campaigns create-from-export --campaign-id ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST` | `/campaigns/{id}/export` | https://developer.instantly.ai/api/v2/campaign/exportcampaign | `instantly-api-tool campaigns export --campaign-id ...` | implemented | Write-capable; apply-gated |
| `POST` | `/campaigns/{id}/duplicate` | https://developer.instantly.ai/api/v2/campaign/duplicate | `instantly-api-tool campaigns duplicate --campaign-id ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `GET` | `/campaigns/count-launched` | https://developer.instantly.ai/api/v2/campaign/countlaunched | `instantly-api-tool campaigns count-launched` | implemented | Read-only |
| `POST` | `/campaigns/{id}/variables` | https://developer.instantly.ai/api/v2/campaign/addvariables | `instantly-api-tool campaigns add-variables --campaign-id ... --file ...` | implemented | Write; apply-gated |
| `GET` | `/lead-lists/{id}/verification-stats` | https://developer.instantly.ai/api/v2/leadlist/getverificationstats | `instantly-api-tool lead-lists verification-stats --lead-list-id ...` | implemented | Read-only |
| `POST` | `/leads` | https://developer.instantly.ai/api/v2/lead/createlead | `instantly-api-tool leads create --file ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `DELETE` | `/leads` | https://developer.instantly.ai/api/v2/lead/bulkdeleteleads | `instantly-api-tool leads bulk-delete --file ...` | implemented | Destructive; apply requires `--yes --plan-in` |
| `PATCH` | `/leads/{id}` | https://developer.instantly.ai/api/v2/lead/patchlead | `instantly-api-tool leads patch --lead-id ... --file ...` | implemented | Write; apply-gated |
| `DELETE` | `/leads/{id}` | https://developer.instantly.ai/api/v2/lead/deletelead | `instantly-api-tool leads delete --lead-id ...` | implemented | Destructive; apply requires `--yes --plan-in` |
| `POST` | `/leads/merge` | https://developer.instantly.ai/api/v2/lead/mergeleads | `instantly-api-tool leads merge --file ...` | implemented | Destructive-ish; apply requires `--yes --plan-in` |
| `POST` | `/leads/update-interest-status` | https://developer.instantly.ai/api/v2/lead/updateleadintereststatus | `instantly-api-tool leads update-interest-status --file ...` | implemented | Potentially batch; apply requires `--yes` |
| `POST` | `/leads/subsequence/remove` | https://developer.instantly.ai/api/v2/lead/removeleadfromsubsequence | `instantly-api-tool leads remove-from-subsequence --file ...` | implemented | Write; apply requires `--yes` |
| `POST` | `/leads/bulk-assign` | https://developer.instantly.ai/api/v2/lead/bulkassignleads | `instantly-api-tool leads bulk-assign --file ...` | implemented | Batch; apply requires `--yes` |
| `POST` | `/leads/move` | https://developer.instantly.ai/api/v2/lead/moveleads | `instantly-api-tool leads move --file ...` | implemented | Batch; apply requires `--yes` |
| `POST` | `/leads/subsequence/move` | https://developer.instantly.ai/api/v2/lead/moveleadtosubsequence | `instantly-api-tool leads move-to-subsequence --file ...` | implemented | Write; apply requires `--yes` |
| `GET` | `/subsequences/{id}/sending-status` | https://developer.instantly.ai/api/v2/campaignsubsequence/getsubsequencesendingstatus | `instantly-api-tool subsequences sending-status --subsequence-id ...` | implemented | Read-only |
| `POST` | `/subsequences/{id}/duplicate` | https://developer.instantly.ai/api/v2/campaignsubsequence/duplicatesubsequence | `instantly-api-tool subsequences duplicate --subsequence-id ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST` | `/subsequences/{id}/pause` | https://developer.instantly.ai/api/v2/campaignsubsequence/pausesubsequence | `instantly-api-tool subsequences pause --subsequence-id ...` | implemented | Write; apply-gated |
| `POST` | `/subsequences/{id}/resume` | https://developer.instantly.ai/api/v2/campaignsubsequence/resumesubsequence | `instantly-api-tool subsequences resume --subsequence-id ...` | implemented | Write; apply-gated |
| `GET` | `/webhooks/{id}` | https://developer.instantly.ai/api/v2/webhook/getwebhook | `instantly-api-tool webhooks get --webhook-id ...` | implemented | Read-only |
| `GET` | `/webhooks/event-types` | https://developer.instantly.ai/api/v2/webhook/listwebhookeventtypes | `instantly-api-tool webhooks event-types` | implemented | Read-only |
| `POST` | `/webhooks/{id}/resume` | https://developer.instantly.ai/api/v2/webhook/resumewebhook | `instantly-api-tool webhooks resume --webhook-id ...` | implemented | Write; apply-gated |
| `GET` | `/block-lists-entries/{id}` | https://developer.instantly.ai/api/v2/blocklistentry/getblocklistentry | `instantly-api-tool do-not-contact get --entry-id ...` | implemented | Read-only |
| `PATCH` | `/block-lists-entries/{id}` | https://developer.instantly.ai/api/v2/blocklistentry/patchblocklistentry | `instantly-api-tool do-not-contact patch --entry-id ... --file ...` | implemented | Write; apply requires `--yes` |
| `POST` | `/supersearch-enrichment` | https://developer.instantly.ai/api/v2/supersearchenrichment/createsupersearchenrichment | `instantly-api-tool supersearch-enrichment create --file ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `GET` | `/supersearch-enrichment/{resource_id}` | https://developer.instantly.ai/api/v2/supersearchenrichment/getenrichmentforresource | `instantly-api-tool supersearch-enrichment get --resource-id ...` | implemented | Read-only |
| `PATCH` | `/supersearch-enrichment/{resource_id}/settings` | https://developer.instantly.ai/api/v2/supersearchenrichment/updateenrichmentsettingsforresource | `instantly-api-tool supersearch-enrichment patch-settings --resource-id ... --file ...` | implemented | Advanced; apply requires `--yes` |
| `GET` | `/supersearch-enrichment/history/{resource_id}` | https://developer.instantly.ai/api/v2/supersearchenrichment/getenrichmenthistory | `instantly-api-tool supersearch-enrichment history --resource-id ...` | implemented | Read-only |
| `POST` | `/supersearch-enrichment/run` | https://developer.instantly.ai/api/v2/supersearchenrichment/runenrichment | `instantly-api-tool supersearch-enrichment run --file ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST` | `/supersearch-enrichment/enrich-leads-from-supersearch` | https://developer.instantly.ai/api/v2/supersearchenrichment/enrichleadsfromsupersearch | `instantly-api-tool supersearch-enrichment enrich-leads --file ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST` | `/supersearch-enrichment/ai` | https://developer.instantly.ai/api/v2/supersearchenrichment/createaienrichment | `instantly-api-tool supersearch-enrichment ai --file ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST` | `/supersearch-enrichment/count-leads-from-supersearch` | https://developer.instantly.ai/api/v2/supersearchenrichment/countleadsfromsupersearch | `instantly-api-tool supersearch-enrichment count-leads --file ...` | implemented | Treated as read-only query (even though POST) |
| `POST` | `/supersearch-enrichment/preview-leads-from-supersearch` | https://developer.instantly.ai/api/v2/supersearchenrichment/previewleadsfromsupersearch | `instantly-api-tool supersearch-enrichment preview-leads --file ...` | implemented | Treated as read-only query (even though POST) |
| `POST` | `/emails/forward` | https://developer.instantly.ai/api/v2/email/forwardemail | `instantly-api-tool emails forward --file ...` | implemented | Plan-first; live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PATCH` | `/emails/{id}` | https://developer.instantly.ai/api/v2/email/patchemail | `instantly-api-tool emails patch --email-id ... --file ...` | implemented | Write; apply-gated; verifies via GET after PATCH |
| `DELETE` | `/emails/{id}` | https://developer.instantly.ai/api/v2/email/deleteemail | `instantly-api-tool emails delete --email-id ...` | implemented | Destructive; apply requires `--yes --plan-in`; verifies best-effort via GET expecting 404 |

## Endpoint coverage

Columns:
- Endpoint
- Capability
- CLI command(s)
- Safety gates (dry-run/apply/yes)
- Tests/examples
- Notes

| Endpoint | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| `GET /workspaces/current` | Current workspace | `instantly-api-tool whoami` / `health` / `auth check` | read-only | `tests/test_instantly_commands.py` | Docs: `docs/references.md` |
| `PATCH /workspaces/current` | Update current workspace | `instantly-api-tool workspace patch-current --file ...` | dry-run plan; apply-gated (`--apply --plan-in ...`) | `tests/test_instantly_commands.py` | Irreversible risk varies by fields; require plan-in on apply |
| `POST /workspaces/create` | Create a workspace | `instantly-api-tool workspace create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /workspaces/current/change-owner` | Change workspace owner | `instantly-api-tool workspace change-owner --file ...` | dry-run plan; apply-gated (`--apply --plan-in ...`) | `tests/test_instantly_commands.py` | Owner changes are high-impact; plan-in required |
| `GET /workspaces/current/whitelabel-domain` | Get current whitelabel domain | `instantly-api-tool workspace whitelabel-domain get` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /workspaces/current/whitelabel-domain` | Set current whitelabel domain | `instantly-api-tool workspace whitelabel-domain set --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Best-effort verify by GET |
| `DELETE /workspaces/current/whitelabel-domain` | Delete current whitelabel domain | `instantly-api-tool workspace whitelabel-domain delete` | dry-run plan; apply-gated (`--apply --yes --plan-in ...`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `GET /workspace-billing/plan-details` | Workspace plan details | `instantly-api-tool workspace-billing plan-details` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /workspace-billing/subscription-details` | Workspace subscription details | `instantly-api-tool workspace-billing subscription-details` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /workspace-members` | List workspace members | `instantly-api-tool workspace-members list` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /workspace-members/{id}` | Get workspace member | `instantly-api-tool workspace-members get --id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /workspace-members` | Create workspace member | `instantly-api-tool workspace-members create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /workspace-members/{id}` | Patch workspace member | `instantly-api-tool workspace-members patch --id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Best-effort verify by GET by id |
| `DELETE /workspace-members/{id}` | Delete workspace member | `instantly-api-tool workspace-members delete --id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in ...`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `GET /workspace-group-members` | List workspace group members | `instantly-api-tool workspace-group-members list` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /workspace-group-members/admin` | List admin group memberships | `instantly-api-tool workspace-group-members admin` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /workspace-group-members/{id}` | Get workspace group member | `instantly-api-tool workspace-group-members get --id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /workspace-group-members` | Create workspace group member | `instantly-api-tool workspace-group-members create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `DELETE /workspace-group-members/{id}` | Delete workspace group member | `instantly-api-tool workspace-group-members delete --id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in ...`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `POST /oauth/google/init` | Start Google OAuth session | `instantly-api-tool oauth google-init --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /oauth/microsoft/init` | Start Microsoft OAuth session | `instantly-api-tool oauth microsoft-init --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /oauth/session/status/{sessionId}` | OAuth session status | `instantly-api-tool oauth session-status --session-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /crm-actions/phone-numbers` | List CRM phone numbers | `instantly-api-tool crm-actions list-phone-numbers` | read-only | `tests/test_instantly_commands.py` |  |
| `DELETE /crm-actions/phone-numbers/{id}` | Delete CRM phone number | `instantly-api-tool crm-actions delete-phone-number --id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in ...`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `GET /dfy-email-account-orders` | List DFY email account orders | `instantly-api-tool dfy-email-account-orders list-orders` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /dfy-email-account-orders/accounts` | List DFY email accounts | `instantly-api-tool dfy-email-account-orders list-accounts [--with-passwords]` | read-only; secret-bearing requires local store ack | `tests/test_instantly_commands.py` | With passwords: file-only output |
| `POST /dfy-email-account-orders` | Create DFY order | `instantly-api-tool dfy-email-account-orders create-order --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /dfy-email-account-orders/accounts/cancel` | Cancel DFY accounts | `instantly-api-tool dfy-email-account-orders cancel-accounts --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /dfy-email-account-orders/domains/check` | Check domains | `instantly-api-tool dfy-email-account-orders check-domains --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` |  |
| `POST /dfy-email-account-orders/domains/similar` | Similar domains | `instantly-api-tool dfy-email-account-orders similar-domains --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` |  |
| `POST /dfy-email-account-orders/domains/pre-warmed-up-list` | Prewarmed domains | `instantly-api-tool dfy-email-account-orders prewarmed-domains` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /api-keys` | List API keys | `instantly-api-tool api-keys list` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /api-keys` | Create API key (secret-safe) | `instantly-api-tool api-keys create --file ...` | dry-run plan; apply-gated (`--apply --yes --plan-in ... --ack-store-secret-locally`) | `tests/test_instantly_commands.py` | Any raw key/token is stored file-only |
| `DELETE /api-keys/{id}` | Delete API key | `instantly-api-tool api-keys delete --id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in ...`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `GET /campaigns` | List campaigns | `instantly-api-tool campaigns list` | read-only | `tests/test_instantly_commands.py` | Docs explorer uses `campaign/listcampaign` naming |
| `GET /campaigns/{campaign_id}` | Get campaign | `instantly-api-tool campaigns get --campaign-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /campaigns` | Create campaign | `instantly-api-tool campaigns create --file ...` | plan-first; explicit no-snapshot approval required | `examples/campaign_create.json` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /campaigns/{campaign_id}/activate` | Activate campaign | `instantly-api-tool campaigns activate --campaign-id ...` | dry-run plan; apply-gated (`--apply`) + before-state | `tests/test_instantly_commands.py` | Verify: GET `/campaigns/{id}` |
| `POST /campaigns/{campaign_id}/pause` | Pause campaign | `instantly-api-tool campaigns pause --campaign-id ...` | dry-run plan; apply-gated (`--apply`) + before-state | `tests/test_instantly_commands.py` | Verify: GET `/campaigns/{id}` |
| `PATCH /campaigns/{campaign_id}` | Patch campaign | `instantly-api-tool campaigns patch --campaign-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `DELETE /campaigns/{campaign_id}` | Delete campaign | `instantly-api-tool campaigns delete --campaign-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `GET /campaigns/{campaign_id}/sending-status` | Campaign sending status | `instantly-api-tool campaigns sending-status --campaign-id ...` | read-only | `tests/test_instantly_commands.py` | Optional query: `with_ai_summary` |
| `GET /campaigns/search-by-contact` | Search campaigns by lead email | `instantly-api-tool campaigns search-by-contact --email ...` | read-only | `tests/test_instantly_commands.py` | Query uses `search=<email>` |
| `POST /campaigns/{campaign_id}/share` | Share campaign | `instantly-api-tool campaigns share --campaign-id ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-impact; requires `--yes` on apply |
| `POST /campaigns/{campaign_id}/from-export` | Create campaign from export | `instantly-api-tool campaigns create-from-export --campaign-id ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /campaigns/{campaign_id}/export` | Export campaign | `instantly-api-tool campaigns export --campaign-id ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Response-only |
| `POST /campaigns/{campaign_id}/duplicate` | Duplicate campaign | `instantly-api-tool campaigns duplicate --campaign-id ... --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /campaigns/count-launched` | Count launched campaigns | `instantly-api-tool campaigns count-launched` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /campaigns/{campaign_id}/variables` | Add campaign variables | `instantly-api-tool campaigns add-variables --campaign-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `POST /accounts/warmup-analytics` | Warmup analytics | `instantly-api-tool analytics warmup ...` | read-only | `tests/test_instantly_commands.py` | Body: `emails[]` |
| `GET /accounts/analytics/daily` | Daily account analytics | `instantly-api-tool analytics accounts-daily ...` | read-only | `tests/test_instantly_commands.py` | Query: `emails`, `start_date`, `end_date` |
| `POST /accounts/test/vitals` | Account vitals (diagnostic) | `instantly-api-tool analytics account-vitals ...` | read-only | `tests/test_instantly_commands.py` | Body: `emails[]` |
| `GET /campaigns/analytics` | Campaign analytics | `instantly-api-tool analytics campaigns ...` | read-only | `tests/test_instantly_commands.py` | Query: `start_date`, `end_date`; optional `id/ids` |
| `GET /campaigns/analytics/overview` | Campaign analytics overview | `instantly-api-tool analytics campaigns-overview ...` | read-only | `tests/test_instantly_commands.py` | Query: `start_date`, `end_date`; optional `id/ids`, `campaign_status` |
| `GET /campaigns/analytics/daily` | Daily campaign analytics | `instantly-api-tool analytics campaigns-daily ...` | read-only | `tests/test_instantly_commands.py` | Query: `campaign_id`, `start_date`, `end_date` |
| `GET /campaigns/analytics/steps` | Campaign steps analytics | `instantly-api-tool analytics campaign-steps ...` | read-only | `tests/test_instantly_commands.py` | Query: `campaign_id`, `start_date`, `end_date` |
| `POST /leads/list` | List leads | `instantly-api-tool leads list [--campaign-id ...]` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /leads/{lead_id}` | Get lead | `instantly-api-tool leads get --lead-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /leads` | Create lead | `instantly-api-tool leads create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /leads/{lead_id}` | Patch lead | `instantly-api-tool leads patch --lead-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `DELETE /leads/{lead_id}` | Delete lead | `instantly-api-tool leads delete --lead-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `DELETE /leads` | Bulk delete leads | `instantly-api-tool leads bulk-delete --file ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Destructive; plan-in required |
| `POST /leads/merge` | Merge leads | `instantly-api-tool leads merge --file ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Destructive-ish; plan-in required |
| `POST /leads/update-interest-status` | Update lead interest status | `instantly-api-tool leads update-interest-status --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-risk/batch; requires `--yes` |
| `POST /leads/subsequence/remove` | Remove leads from subsequence | `instantly-api-tool leads remove-from-subsequence --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-risk/batch; requires `--yes` |
| `POST /leads/bulk-assign` | Bulk assign leads | `instantly-api-tool leads bulk-assign --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-risk/batch; requires `--yes` |
| `POST /leads/move` | Move leads | `instantly-api-tool leads move --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-risk/batch; requires `--yes` |
| `POST /leads/subsequence/move` | Move leads to subsequence | `instantly-api-tool leads move-to-subsequence --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-risk/batch; requires `--yes` |
| `POST /leads/add` | Bulk add leads | `instantly-api-tool leads add-bulk --campaign-id ... (--csv ... | --json ...)` | plan-first; explicit no-snapshot approval required | `examples/leads.csv`, `examples/leads.json` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /supersearch-enrichment` | Create supersearch enrichment | `instantly-api-tool supersearch-enrichment create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /supersearch-enrichment/{resource_id}` | Get supersearch enrichment | `instantly-api-tool supersearch-enrichment get --resource-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `PATCH /supersearch-enrichment/{resource_id}/settings` | Patch enrichment settings | `instantly-api-tool supersearch-enrichment patch-settings --resource-id ... --file ...` | dry-run plan; apply-gated (`--apply --yes`) + before-state | `tests/test_instantly_commands.py` | Verify: best-effort GET `/supersearch-enrichment/{resource_id}` after apply |
| `GET /supersearch-enrichment/history/{resource_id}` | Get enrichment history | `instantly-api-tool supersearch-enrichment history --resource-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /supersearch-enrichment/run` | Run enrichment | `instantly-api-tool supersearch-enrichment run --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /supersearch-enrichment/enrich-leads-from-supersearch` | Enrich leads from supersearch | `instantly-api-tool supersearch-enrichment enrich-leads --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /supersearch-enrichment/ai` | Create AI enrichment | `instantly-api-tool supersearch-enrichment ai --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /supersearch-enrichment/count-leads-from-supersearch` | Count leads from supersearch | `instantly-api-tool supersearch-enrichment count-leads --file ...` | read-only | `tests/test_instantly_commands.py` | Read-only query (uses POST) |
| `POST /supersearch-enrichment/preview-leads-from-supersearch` | Preview leads from supersearch | `instantly-api-tool supersearch-enrichment preview-leads --file ...` | read-only | `tests/test_instantly_commands.py` | Read-only query (uses POST) |
| `POST /inbox-placement-tests` | Create inbox placement test | `instantly-api-tool inbox-placement tests create ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /inbox-placement-tests` | List inbox placement tests | `instantly-api-tool inbox-placement tests list ...` | read-only | `tests/test_instantly_commands.py` | Safe defaults: `--limit 20` (max 50) |
| `GET /inbox-placement-tests/{test_id}` | Get inbox placement test | `instantly-api-tool inbox-placement tests get --test-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `PATCH /inbox-placement-tests/{test_id}` | Patch inbox placement test | `instantly-api-tool inbox-placement tests patch --test-id ... --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` |  |
| `DELETE /inbox-placement-tests/{test_id}` | Delete inbox placement test | `instantly-api-tool inbox-placement tests delete --test-id ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` |  |
| `GET /inbox-placement-tests/email-service-provider-options` | List inbox placement ESP options | `instantly-api-tool inbox-placement tests esp-options` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /inbox-placement-analytics` | List inbox placement analytics | `instantly-api-tool inbox-placement analytics list ...` | read-only | `tests/test_instantly_commands.py` | Requires `--test-id` to avoid broad queries |
| `GET /inbox-placement-analytics/{analytics_id}` | Get inbox placement analytics | `instantly-api-tool inbox-placement analytics get --analytics-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /inbox-placement-analytics/stats-by-test-id` | Inbox placement stats by test id | `instantly-api-tool inbox-placement analytics stats-by-test-id ...` | read-only | `tests/test_instantly_commands.py` | Body: `test_id` |
| `POST /inbox-placement-analytics/deliverability-insights` | Inbox placement deliverability insights | `instantly-api-tool inbox-placement analytics deliverability-insights ...` | read-only | `tests/test_instantly_commands.py` | Body: `test_id` |
| `POST /inbox-placement-analytics/stats-by-date` | Inbox placement stats by date | `instantly-api-tool inbox-placement analytics stats-by-date ...` | read-only | `tests/test_instantly_commands.py` | Body: `test_id` |
| `GET /inbox-placement-reports` | List inbox placement reports (blacklist + spamassassin) | `instantly-api-tool inbox-placement reports list ...` | read-only | `tests/test_instantly_commands.py` | Requires `--test-id` to avoid broad queries |
| `GET /inbox-placement-reports/{report_id}` | Get inbox placement report (blacklist + spamassassin) | `instantly-api-tool inbox-placement reports get --report-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /webhooks` | List webhooks | `instantly-api-tool webhooks list` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /webhooks/{webhook_id}` | Get webhook | `instantly-api-tool webhooks get --webhook-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /webhooks/event-types` | List webhook event types | `instantly-api-tool webhooks event-types` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /webhooks` | Create webhook | `instantly-api-tool webhooks create --file ...` | plan-first; explicit no-snapshot approval required | `examples/webhook_create.json` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /webhooks/{webhook_id}` | Patch webhook | `instantly-api-tool webhooks patch --webhook-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` |  |
| `DELETE /webhooks/{webhook_id}` | Delete webhook | `instantly-api-tool webhooks delete --webhook-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `POST /webhooks/{webhook_id}/test` | Send test webhook | `instantly-api-tool webhooks test --webhook-id ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /webhooks/{webhook_id}/resume` | Resume webhook delivery | `instantly-api-tool webhooks resume --webhook-id ...` | dry-run plan; apply-gated (`--apply`) + before-state | `tests/test_instantly_commands.py` |  |
| `GET /webhook-events` | List webhook events | `instantly-api-tool webhook-events list [--webhook-id ...]` | read-only | `tests/test_instantly_commands.py` | Safe defaults: `--limit 20` (max 50) |
| `GET /webhook-events/{event_id}` | Get webhook event | `instantly-api-tool webhook-events get --event-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /webhook-events/summary` | Webhook events summary (overview aggregates) | `instantly-api-tool webhook-events summary --from ... --to ...` | read-only | `tests/test_instantly_commands.py` | Requires `--from/--to` (YYYY-MM-DD) |
| `GET /webhook-events/summary-by-date` | Webhook events summary by date | `instantly-api-tool webhook-events summary-by-date --from ... --to ...` | read-only | `tests/test_instantly_commands.py` | Requires `--from/--to` (YYYY-MM-DD) |
| `GET /emails` | List emails | `instantly-api-tool emails list` | read-only | `tests/test_instantly_commands.py` | Default `--limit` is `20` (email endpoints are rate-limit-sensitive in Instantly docs) |
| `GET /emails/{email_id}` | Get email | `instantly-api-tool emails get --email-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /emails/unread/count` | Unread count | `instantly-api-tool emails unread-count` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /email-verification` | Create email verification | `instantly-api-tool email-verification create ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /email-verification/{email}` | Check email verification status | `instantly-api-tool email-verification status --email ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /emails/threads/{thread_id}/mark-as-read` | Mark a thread as read | `instantly-api-tool threads mark-as-read --thread-id ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `POST /emails/reply` | Reply to a thread (irreversible) | `instantly-api-tool threads reply ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /audit-logs` | List audit log events | `instantly-api-tool audit-log list ...` | read-only | `tests/test_instantly_commands.py` | Raw items hidden by default; use `--include-items --out <path>` (file-only) |
| `GET /block-lists-entries` | List do-not-contact entries | `instantly-api-tool do-not-contact list` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /block-lists-entries/{entry_id}` | Get do-not-contact entry | `instantly-api-tool do-not-contact get --entry-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /block-lists-entries` | Add do-not-contact entry | `instantly-api-tool do-not-contact create --email ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /block-lists-entries/{entry_id}` | Patch do-not-contact entry | `instantly-api-tool do-not-contact patch --entry-id ... --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | High-risk; requires `--yes` on apply |
| `DELETE /block-lists-entries/{entry_id}` | Delete do-not-contact entry | `instantly-api-tool do-not-contact delete --entry-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `GET /background-jobs` | List background jobs | `instantly-api-tool background-jobs list` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /background-jobs/{job_id}` | Get background job | `instantly-api-tool background-jobs get --job-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /accounts` | List accounts | `instantly-api-tool accounts list` | dry-run plan; apply-gated (`--apply --yes`); file-only output | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /accounts/{email}` | Get account | `instantly-api-tool accounts get --email ...` | dry-run plan; apply-gated (`--apply --yes`); file-only output | `tests/test_instantly_commands.py` | Receipt output is redacted for sensitive keys |
| `POST /accounts` | Create account | `instantly-api-tool accounts create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /accounts/{email}` | Patch account | `instantly-api-tool accounts patch --email ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Plan/request body is redacted for sensitive keys |
| `DELETE /accounts/{email}` | Delete account | `instantly-api-tool accounts delete --email ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `POST /accounts/warmup/enable` | Enable warmup (batch) | `instantly-api-tool accounts warmup-enable --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | Batch write |
| `POST /accounts/warmup/disable` | Disable warmup (batch) | `instantly-api-tool accounts warmup-disable --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | Batch write |
| `POST /accounts/{email}/pause` | Pause account | `instantly-api-tool accounts pause --email ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` |  |
| `POST /accounts/{email}/resume` | Resume account | `instantly-api-tool accounts resume --email ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` |  |
| `POST /accounts/{email}/mark-fixed` | Mark account fixed | `instantly-api-tool accounts mark-fixed --email ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` |  |
| `POST /accounts/test/vitals` | Test account vitals | `instantly-api-tool accounts test-vitals --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Treat response as sensitive; output is redacted |
| `GET /accounts/ctd/status` | CTD status | `instantly-api-tool accounts ctd-status` | dry-run plan; apply-gated (`--apply --yes`); file-only output | `tests/test_instantly_commands.py` | Treat response as sensitive; receipt output is redacted |
| `POST /accounts/move` | Move accounts | `instantly-api-tool accounts move --file ...` | dry-run plan; apply-gated (`--apply --yes`) | `tests/test_instantly_commands.py` | Batch write |
| `GET /lead-lists` | List lead lists | `instantly-api-tool lead-lists list` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /lead-lists/{id}` | Get lead list | `instantly-api-tool lead-lists get --lead-list-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `GET /lead-lists/{id}/verification-stats` | Lead list verification stats | `instantly-api-tool lead-lists verification-stats --lead-list-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /lead-lists` | Create lead list | `instantly-api-tool lead-lists create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /lead-lists/{id}` | Patch lead list | `instantly-api-tool lead-lists patch --lead-list-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `DELETE /lead-lists/{id}` | Delete lead list | `instantly-api-tool lead-lists delete --lead-list-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `POST /lead-labels` | Create lead label | `instantly-api-tool lead-labels create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /lead-labels` | List lead labels | `instantly-api-tool lead-labels list` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /lead-labels/{id}` | Get lead label | `instantly-api-tool lead-labels get --lead-label-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `PATCH /lead-labels/{id}` | Patch lead label | `instantly-api-tool lead-labels patch --lead-label-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `DELETE /lead-labels/{id}` | Delete lead label | `instantly-api-tool lead-labels delete --lead-label-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `POST /custom-tags` | Create custom tag | `instantly-api-tool custom-tags create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /custom-tags` | List custom tags | `instantly-api-tool custom-tags list` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /custom-tags/{id}` | Get custom tag | `instantly-api-tool custom-tags get --tag-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `PATCH /custom-tags/{id}` | Patch custom tag | `instantly-api-tool custom-tags patch --tag-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `DELETE /custom-tags/{id}` | Delete custom tag | `instantly-api-tool custom-tags delete --tag-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `POST /custom-tags/toggle-resource` | Toggle tag mapping | `instantly-api-tool custom-tags toggle-resource --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `GET /custom-tag-mappings` | List custom tag mappings | `instantly-api-tool custom-tag-mappings list` | read-only | `tests/test_instantly_commands.py` | Mapping endpoints are read-only in official docs |
| `GET /account-campaign-mappings/{email}` | Get account campaign mapping | `instantly-api-tool account-campaign-mappings get --email ...` | read-only | `tests/test_instantly_commands.py` | Read-only in official docs |
| `GET /subsequences` | List subsequences | `instantly-api-tool subsequences list` | read-only | `tests/test_instantly_commands.py` | Pagination supported |
| `GET /subsequences/{id}` | Get subsequence | `instantly-api-tool subsequences get --subsequence-id ...` | read-only | `tests/test_instantly_commands.py` |  |
| `POST /subsequences` | Create subsequence | `instantly-api-tool subsequences create --file ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |
| `PATCH /subsequences/{id}` | Patch subsequence | `instantly-api-tool subsequences patch --subsequence-id ... --file ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `DELETE /subsequences/{id}` | Delete subsequence | `instantly-api-tool subsequences delete --subsequence-id ...` | dry-run plan; apply-gated (`--apply --yes --plan-in`) | `tests/test_instantly_commands.py` | Delete apply requires plan-file workflow |
| `GET /subsequences/{id}/sending-status` | Subsequence sending status | `instantly-api-tool subsequences sending-status --subsequence-id ...` | read-only | `tests/test_instantly_commands.py` | Optional query: `with_ai_summary` |
| `POST /subsequences/{id}/pause` | Pause subsequence | `instantly-api-tool subsequences pause --subsequence-id ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `POST /subsequences/{id}/resume` | Resume subsequence | `instantly-api-tool subsequences resume --subsequence-id ...` | dry-run plan; apply-gated (`--apply`) | `tests/test_instantly_commands.py` | Verify: best-effort GET by id |
| `POST /subsequences/{id}/duplicate` | Duplicate subsequence | `instantly-api-tool subsequences duplicate --subsequence-id ...` | plan-first; explicit no-snapshot approval required | `tests/test_instantly_commands.py` | Needs saved before-state or explicit no-snapshot approval before live apply |

## Known gaps (explicit)

- Unsupported write families need either a safe before-state pre-read, explicit no-snapshot approval with a clear receipt, or a real blocker reason if the command cannot safely execute the action.
- Templates/flows (`customprompttemplate`, `salesflow`, `emailtemplate`) — docs mismatch (schema-only as of 2026-02-19); implementing would require guessing.
