# Command reference

Use this page when you need the exact CallRail command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `qwayk-callrail-safe-agent-cli onboarding [--no-write-env]`

## Auth

- `qwayk-callrail-safe-agent-cli --output json --version`
- `qwayk-callrail-safe-agent-cli auth check`

## Runs (local history)

- `qwayk-callrail-safe-agent-cli runs list [--limit 20]`
- `qwayk-callrail-safe-agent-cli runs show --run-id <run_id>`

## API command families currently shipped

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Most REST commands in this tool are account-scoped.
In normal use, include `--account-id` on those commands.
Use it as `--account-id <account_id>`.
You can omit it only when `CALLRAIL_DEFAULT_ACCOUNT_ID` is already set in your `.env`.

Optional flags:
- `--output json`: machine-readable output mode
- `--env-file <path>`: choose a specific `.env` file
- `--timeout-s <seconds>`: override timeout for one run
- `--verbose`: show HTTP request start/end lines on stderr
- `--debug`: show Python stack traces for debugging
- `--apply`: turn a write from dry-run into a live request
- `--yes`: required for live writes
- `--ack-no-snapshot`: required for live writes while this tool has no command-specific before-state snapshot
- `--ack-irreversible`: extra acknowledgement for `calls create-outbound` and `text-messages send`
- `--plan-out <path>`: save the dry-run plan to a JSON file
- `--plan-in <path>`: validate a live apply against a saved plan file
- `--receipt-out <path>`: save the post-apply receipt to a JSON file
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- All commands below are in the shared form:
  - Account-scoped read: `qwayk-callrail-safe-agent-cli <family> <command> --account-id <account_id> [id/query flags]`
  - Account-scoped write with a request body: `qwayk-callrail-safe-agent-cli --plan-out plan.json <family> <command> --account-id <account_id> ... --payload-json <json>`
  - Account-scoped write apply with a request body: `qwayk-callrail-safe-agent-cli --apply --yes --ack-no-snapshot --plan-in plan.json <family> <command> --account-id <account_id> ... --payload-json <json>`
  - Account-scoped bodyless delete/disable: `qwayk-callrail-safe-agent-cli --apply --yes --ack-no-snapshot <family> <command> --account-id <account_id> ...`

### Shipped query parameters

Use `--page`, `--per-page`, `--sort`, `--order`, `--search`, `--fields`, `--date-range`, `--start-date`, `--end-date`, `--time-zone`, `--relative-pagination`, and `--offset` where the endpoint supports them.

Shipped read endpoints with additional filters:

- `accounts list`: `--hipaa-account`
- `accounts get`: `--fields` (official documented extra field: `numeric_id`)
- `calls list`: `--company-id`, `--tracker-id`, `--call-type`, `--answer-status`, `--device`, `--direction`, `--lead-status`, `--tags`
- `calls get`: `--fields`
- `companies list`: `--status`
- `companies list` also supports shared query params, including `--search`
- `companies get`: `--fields` (official documented extra field: `verified_caller_ids`)
- `form-submissions list`: `--page`, `--per-page`, `--company-id`, `--person-lead`, `--lead-status`, `--tags`
- `form-submissions list` also supports `--sort`, `--order`, `--fields`, `--date-range`, `--start-date`, `--end-date`, `--time-zone`
- `form-submissions summary`: `--company-id`, `--group-by`, `--fields`, `--tags`, `--custom-form-ids`, `--form-url`, `--lead-status`, `--date-range`, `--start-date`, `--end-date`, `--time-zone`
- `integrations list`: `--page`, `--per-page`, `--company-id` (required), `--fields`
- `integrations get`: `--fields` (official documented extra field: `signing_key`)
- `integration-filters list`: `--page`, `--per-page`, `--company-id` (required)
- `notifications list`: `--page`, `--per-page`, `--notification-type`
- `outbound-caller-ids list`: `--page`, `--per-page`, `--company-id` (required)
- `page-views list`: `--page`, `--per-page`, `--time-zone`
- `sms-threads list`: `--page`, `--per-page`, `--company-id`, `--search`, `--date-range`, `--start-date`, `--end-date`, `--fields`
- `sms-threads get`: `--page`, `--per-page`, `--with-msg-errors`, `--fields`
- `summary-emails list`: `--page`, `--per-page`, `--frequency`, `--company-id`, `--user-id`, `--email`
- `text-messages list`: `--page`, `--per-page`, `--company-id`, `--date-range`, `--start-date`, `--end-date`, `--time-zone`, `--search`, `--fields`
- `text-messages get`: `--fields`
- `message-flows list`: `--page`, `--per-page`, `--company-id`
- `trackers get`: `--fields` (official documented extra fields include `campaign_name`, `swap_targets`)
- `trackers list`: `--page`, `--per-page`, `--company-id`, `--type`, `--status`, `--search`, `--fields`, `--sort`, `--order`
- `users list`: `--page`, `--per-page`, `--company-id`, `--sort`, `--order`, `--search`
- `leads list`: `--page`, `--per-page`, `--company-id`, `--fields`, `--sort`, `--order`
- `calls summary`: `--company-id`, `--group-by`, `--fields`, `--device`, `--min-duration`, `--max-duration`, `--tags`, `--tracker-ids`, `--direction`, `--answer-status`, `--first-time-callers`, `--lead-status`, `--agent`, `--date-range`, `--start-date`, `--end-date`, `--time-zone`, `--search`
- `calls timeseries`: `--company-id`, `--fields`, `--device`, `--interval`, `--min-duration`, `--max-duration`, `--tags`, `--tracker-ids`, `--direction`, `--answer-status`, `--first-time-callers`, `--lead-status`, `--agent`, `--date-range`, `--start-date`, `--end-date`, `--time-zone`

### accounts
- `qwayk-callrail-safe-agent-cli accounts list`
- `qwayk-callrail-safe-agent-cli accounts get --account-id <account_id> [--fields numeric_id]`

### calls
- `qwayk-callrail-safe-agent-cli calls list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli calls get --account-id <account_id> --call-id <call_id> [--fields company_id,milestones]`
- `qwayk-callrail-safe-agent-cli calls create-outbound --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli calls update --account-id <account_id> --call-id <call_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli calls summary --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli calls timeseries --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli calls recording --account-id <account_id> --call-id <call_id>`
- `calls create-outbound` uses `POST /v3/a/{account_id}/calls.json`. Include `--account-id` unless `CALLRAIL_DEFAULT_ACCOUNT_ID` is already set.

### tags
- `qwayk-callrail-safe-agent-cli tags list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli tags create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli tags update --account-id <account_id> --tag-id <tag_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli tags delete --account-id <account_id> --tag-id <tag_id>`

### companies
- `qwayk-callrail-safe-agent-cli companies list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli companies get --account-id <account_id> --company-id <company_id> [--fields verified_caller_ids]`
- `qwayk-callrail-safe-agent-cli companies create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli companies update --account-id <account_id> --company-id <company_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli companies bulk-update --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli companies disable --account-id <account_id> --company-id <company_id>`

### form-submissions
- `qwayk-callrail-safe-agent-cli form-submissions list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli form-submissions create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli form-submissions update --account-id <account_id> --submission-id <submission_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli form-submissions ignore-fields --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli form-submissions summary --account-id <account_id>`

### integrations
- `qwayk-callrail-safe-agent-cli integrations list --account-id <account_id> --company-id <company_id>`
- `qwayk-callrail-safe-agent-cli integrations get --account-id <account_id> --integration-id <integration_id> [--fields signing_key]`
- `qwayk-callrail-safe-agent-cli integrations create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli integrations update --account-id <account_id> --integration-id <integration_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli integrations disable --account-id <account_id> --integration-id <integration_id>`

### integration-filters
- `qwayk-callrail-safe-agent-cli integration-filters list --account-id <account_id> --company-id <company_id>`
- `qwayk-callrail-safe-agent-cli integration-filters create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli integration-filters get --account-id <account_id> --integration-filter-id <integration_filter_id>`
- `qwayk-callrail-safe-agent-cli integration-filters update --account-id <account_id> --integration-filter-id <integration_filter_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli integration-filters delete --account-id <account_id> --integration-filter-id <integration_filter_id>`

### notifications
- `qwayk-callrail-safe-agent-cli notifications list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli notifications create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli notifications update --account-id <account_id> --notification-id <notification_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli notifications delete --account-id <account_id> --notification-id <notification_id>`

### outbound-caller-ids
- `qwayk-callrail-safe-agent-cli outbound-caller-ids list --account-id <account_id> --company-id <company_id>`
- `qwayk-callrail-safe-agent-cli outbound-caller-ids get --account-id <account_id> --caller-id <caller_id>`
- `qwayk-callrail-safe-agent-cli outbound-caller-ids create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli outbound-caller-ids delete --account-id <account_id> --caller-id <caller_id>`

### page-views
- `qwayk-callrail-safe-agent-cli page-views list --account-id <account_id> --call-id <call_id> [--page <n>] [--per-page <n>] [--time-zone <tz>]`

### sms-threads
- `qwayk-callrail-safe-agent-cli sms-threads list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli sms-threads get --account-id <account_id> --thread-id <thread_id> [--page <n>] [--per-page <n>] [--with-msg-errors true] [--fields messages]`
- `qwayk-callrail-safe-agent-cli sms-threads update --account-id <account_id> --thread-id <thread_id> --payload-json <json>`

### summary-emails
- `qwayk-callrail-safe-agent-cli summary-emails list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli summary-emails create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli summary-emails get --account-id <account_id> --summary-email-id <summary_email_id>`
- `qwayk-callrail-safe-agent-cli summary-emails update --account-id <account_id> --summary-email-id <summary_email_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli summary-emails delete --account-id <account_id> --summary-email-id <summary_email_id>`

### text-messages
- `qwayk-callrail-safe-agent-cli text-messages list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli text-messages get --account-id <account_id> --conversation-id <conversation_id> [--fields source,type,media_urls]`
- `qwayk-callrail-safe-agent-cli text-messages send --account-id <account_id> --payload-json <json> [--media-file <path>]`
- `text-messages send` supports plain SMS, MMS by JSON `media_url`, and MMS by multipart `--media-file`. Do not send both `media_url` and `--media-file` in the same request.

### message-flows
- `qwayk-callrail-safe-agent-cli message-flows list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli message-flows get --account-id <account_id> --message-flow-id <message_flow_id>`
- `qwayk-callrail-safe-agent-cli message-flows create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli message-flows update --account-id <account_id> --message-flow-id <message_flow_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli message-flows delete --account-id <account_id> --message-flow-id <message_flow_id>`

### trackers
- `qwayk-callrail-safe-agent-cli trackers list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli trackers get --account-id <account_id> --tracker-id <tracker_id> [--fields campaign_name,swap_targets]`
- `qwayk-callrail-safe-agent-cli trackers create-session --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli trackers create-source --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli trackers update-session --account-id <account_id> --tracker-id <tracker_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli trackers update-source --account-id <account_id> --tracker-id <tracker_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli trackers disable --account-id <account_id> --tracker-id <tracker_id>`
- `trackers create-session` requires payload `type` `session` and the CLI adds it when omitted.
- `trackers create-source` requires payload `type` `source` and the CLI adds it when omitted.
- `trackers update-session` refuses a conflicting payload `type` if you send one.
- `trackers update-source` refuses a conflicting payload `type` if you send one.

### users
- `qwayk-callrail-safe-agent-cli users list --account-id <account_id>`
- `qwayk-callrail-safe-agent-cli users get --account-id <account_id> --user-id <user_id>`
- `qwayk-callrail-safe-agent-cli users create --account-id <account_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli users update --account-id <account_id> --user-id <user_id> --payload-json <json>`
- `qwayk-callrail-safe-agent-cli users delete --account-id <account_id> --user-id <user_id>`

### leads
- `qwayk-callrail-safe-agent-cli leads list --account-id <account_id>`

### lead-timelines
- `qwayk-callrail-safe-agent-cli lead-timelines get --account-id <account_id> --lead-id <lead_id>`
