# API coverage (endpoints → CLI)

Purpose:
- Make CallRail v3 capabilities measurable.
- Keep the shipped command surface honest and reviewable.
- Keep missing or scoped-out behavior explicit.

Rules:
- Keep this ledger honest: each real API intent has a concrete shipped command or an explicit exclusion.
- If something is not for this CLI surface, mark it as excluded here.
- Link implementation deltas back to `docs/references.md` as needed.

## Summary

- Provider: CallRail
- API surface: v3 REST
- API base URL: `https://api.callrail.com/v3/`
- Auth: `Authorization: Token token=<api_key>`
- Optional partner header: `Request-From: <integrator>`
- Key scope: read-only by default, write access must be explicitly enabled on the token/account
- Last audited (UTC): 2026-06-06
- Coverage mode: implemented command surface with local unit coverage; live CallRail proof still pending
- Single-resource query audit: closed for the currently documented REST read surface shipped by this CLI
- Default rate limits are documented per bucket in `docs/references.md` (general API, SMS send, outbound calls)

Columns:
- Resource
- Endpoint capability
- CLI command(s)
- Status
- Safety gates
- Notes

Status guide:
- `implemented, live-unverified`: shipped in the CLI and covered by local tests, but not yet proved with a live CallRail account in this repo

## Endpoint coverage

| Resource | Capability | CLI command(s) | Status | Safety gates | Notes |
|---|---|---|---|---|---|
| Accounts | List accounts | `accounts list` | implemented, live-unverified | read-only | Supports shared query params and `--hipaa-account` (`hipaa_account`) |
| Accounts | Get account | `accounts get --account-id <id>` | implemented, live-unverified | read-only | Supports `fields`; official documented extra field is `numeric_id` |
| Calls | List calls | `calls list` | implemented, live-unverified | read-only | Supports shared query params plus `company_id`, `tracker_id`, `call_type`, `answer_status`, `device`, `direction`, `lead_status`, `tags` |
| Calls | Get call | `calls get --call-id <id>` | implemented, live-unverified | read-only | Supports `fields`, including additional official fields such as `company_id`, `milestones`, `timeline_url`, `keywords_spotted`, `transcription`, `person_id`, `sentiment`, `zip_code`, and `conversational_transcript` when the account plan allows them |
| Calls | Create outbound call | `calls create-outbound` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot + ack-no-snapshot + ack-irreversible | Uses the account-scoped `POST /v3/a/{account_id}/calls.json` endpoint and the outbound-call rate-limit bucket |
| Calls | Update call | `calls update --call-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Calls | Get call summary | `calls summary` | implemented, live-unverified | read-only | Supports `company_id`, `group_by`, `fields`, `device`, `min_duration`, `max_duration`, `tags`, `tracker_ids`, `direction`, `answer_status`, `first_time_callers`, `lead_status`, `agent`, `date_range`, `start_date`, `end_date`, `time_zone`, `search` |
| Calls | Get calls timeseries | `calls timeseries` | implemented, live-unverified | read-only | Supports `company_id`, `fields`, `device`, `interval`, `min_duration`, `max_duration`, `tags`, `tracker_ids`, `direction`, `answer_status`, `first_time_callers`, `lead_status`, `agent`, `date_range`, `start_date`, `end_date`, `time_zone` |
| Calls | Get recording | `calls recording --call-id <id>` | implemented, live-unverified | read-only | |
| Tags | List tags | `tags list` | implemented, live-unverified | read-only | |
| Tags | Create tag | `tags create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Tags | Update tag | `tags update --tag-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Tags | Delete tag | `tags delete --tag-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Companies | List companies | `companies list` | implemented, live-unverified | read-only | Supports shared query params plus `--status` and `--search` |
| Companies | Get company | `companies get --company-id <id>` | implemented, live-unverified | read-only | Supports `fields`; official documented extra field is `verified_caller_ids` |
| Companies | Create company | `companies create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Companies | Update company | `companies update --company-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Companies | Bulk update | `companies bulk-update` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Companies | Disable company | `companies disable --company-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Form submissions | List form submissions | `form-submissions list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `company_id`, `person_lead`, `lead_status`, `tags`, `sort`, `order`, `fields`, `date_range`, `start_date`, `end_date`, `time_zone` |
| Form submissions | Create form submission | `form-submissions create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Form submissions | Update form submission | `form-submissions update --submission-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Form submissions | Ignore form fields | `form-submissions ignore-fields` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Real POST endpoint that updates future capture behavior and starts a background cleanup job |
| Form submissions | Form submission summary | `form-submissions summary` | implemented, live-unverified | read-only | Supports `company_id`, `group_by`, `fields`, `tags`, `custom_form_ids`, `form_url`, `lead_status`, `date_range`, `start_date`, `end_date`, `time_zone` |
| Integrations | List integrations | `integrations list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, required `company_id`, and `fields` (including `signing_key` for webhook integrations) |
| Integrations | Get integration | `integrations get --integration-id <id>` | implemented, live-unverified | read-only | Supports `fields`; official documented extra field is `signing_key` for webhook integrations |
| Integrations | Create integration | `integrations create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Create/update support is only `webhooks` and `custom`
| Integrations | Update integration | `integrations update --integration-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | API key type check: only `webhooks` / `custom` |
| Integrations | Disable integration | `integrations disable --integration-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Integration filters | List filters | `integration-filters list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, and required `company_id` |
| Integration filters | Create filter | `integration-filters create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Integration filters | Get filter | `integration-filters get --integration-filter-id <id>` | implemented, live-unverified | read-only | |
| Integration filters | Update filter | `integration-filters update --integration-filter-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Integration filters | Delete filter | `integration-filters delete --integration-filter-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Notifications | List notifications | `notifications list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, and `notification_type` |
| Notifications | Create notification | `notifications create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Notifications | Update notification | `notifications update --notification-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Notifications | Delete notification | `notifications delete --notification-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Outbound caller IDs | List caller IDs | `outbound-caller-ids list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, and required `company_id` |
| Outbound caller IDs | Get caller ID | `outbound-caller-ids get --caller-id <id>` | implemented, live-unverified | read-only | |
| Outbound caller IDs | Create caller ID | `outbound-caller-ids create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Outbound caller IDs | Delete caller ID | `outbound-caller-ids delete --caller-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Page views | List page views for a call | `page-views list --call-id <id>` | implemented, live-unverified | read-only | Supports `page`, `per_page`, and `time_zone` |
| SMS threads | List SMS threads | `sms-threads list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `company_id`, `date_range`, `start_date`, `end_date`, `search`, `fields` |
| SMS threads | Get SMS thread | `sms-threads get --thread-id <id>` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `with_msg_errors`, and documented `fields` selection on the paginated thread response |
| SMS threads | Update SMS thread | `sms-threads update --thread-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Summary emails | List summary emails | `summary-emails list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `frequency`, `company_id`, `user_id`, and `email` |
| Summary emails | Create summary email | `summary-emails create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Summary emails | Get summary email | `summary-emails get --summary-email-id <id>` | implemented, live-unverified | read-only | |
| Summary emails | Update summary email | `summary-emails update --summary-email-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Summary emails | Delete summary email | `summary-emails delete --summary-email-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Text messages | List conversations | `text-messages list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `company_id`, `date_range`, `start_date`, `end_date`, `time_zone`, `search`, `fields` |
| Text messages | Get conversation | `text-messages get --conversation-id <id>` | implemented, live-unverified | read-only | Supports `fields`, including newer documented conversation/message fields such as `source`, `type`, and `media_urls` when returned by CallRail |
| Text messages | Send message | `text-messages send` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot + ack-no-snapshot + ack-irreversible | Sends JSON body by default; supports plain SMS, MMS with JSON `media_url`, and MMS with multipart `--media-file`. `media_url` and `--media-file` are mutually exclusive |
| Message flows | List message flows | `message-flows list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, and `company_id` |
| Message flows | Get message flow | `message-flows get --message-flow-id <id>` | implemented, live-unverified | read-only | |
| Message flows | Create message flow | `message-flows create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Keep naming consistent with `create` vs `create-flow` to avoid conflict |
| Message flows | Update message flow | `message-flows update --message-flow-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Message flows | Delete message flow | `message-flows delete --message-flow-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Trackers | List trackers | `trackers list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `company_id`, `type`, `status`, `search`, `fields`, `sort`, and `order` |
| Trackers | Get tracker | `trackers get --tracker-id <id>` | implemented, live-unverified | read-only | Supports `fields`; official documented extra fields include `campaign_name` and `swap_targets` |
| Trackers | Create session tracker | `trackers create-session` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | CLI ensures `type=session` on create |
| Trackers | Create source tracker | `trackers create-source` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | CLI ensures `type=source` on create |
| Trackers | Update session tracker | `trackers update-session --tracker-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Refuses conflicting `payload.type` values |
| Trackers | Update source tracker | `trackers update-source --tracker-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Refuses conflicting `payload.type` values |
| Trackers | Disable tracker | `trackers disable --tracker-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Users | List users | `users list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `company_id`, `sort`, `order`, and `search` |
| Users | Get user | `users get --user-id <id>` | implemented, live-unverified | read-only | |
| Users | Create user | `users create` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Users | Update user | `users update --user-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | |
| Users | Delete user | `users delete --user-id <id>` | implemented, live-unverified | plan first, apply + yes + ack-no-snapshot | Bodyless DELETE (no payload required) |
| Leads | List leads | `leads list` | implemented, live-unverified | read-only | Supports `page`, `per_page`, `company_id`, `fields`, `sort`, and `order` |
| Lead timelines | Get lead timeline | `lead-timelines get --lead-id <id>` | implemented, live-unverified | read-only | Official docs show the path under `/a/{agency_id}/...`; implement with the normal account/agency id input and document the naming quirk |

## Explicit CLI scope exclusions (not in this tool)

- MCP commands
- Generic webhooks test harness / callbacks
- Swap.js examples and generated example payload snippets
- Any docs sample endpoints or sample blocks that are clearly example-only
- Non-REST reference material such as tag color examples, integration setup walkthroughs, tracker provisioning/call-source tables, and user role descriptions

## Notes that affect implementation

- Transcript-related fields may be account-plan gated and should be handled as optional fields in command input/output.
- The summary email docs include at least one sample URL oddity; commands should use API paths from source tables, not copied sample URLs.
- `create`/`update` for integrations are limited to `webhooks` and `custom` types; other types should be rejected early with a clear error.
