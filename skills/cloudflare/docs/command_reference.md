# Command reference

Use this page when you need the exact Cloudflare command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags (selected)

- `--env-file <path>`: which `.env` file to read (default: `.env`)
- `--project-dir <path>`: base directory for safe file outputs (used by sensitive reads)
- `--output json|text`: output mode (default: `json`)
- `--verbose`: log request URLs to stderr (never headers)
- `--progress`: emit periodic "still waiting" lines to stderr on slow requests
- `--timeout-s <seconds>`: override both connect + read timeouts (back-compat)
- `--connect-timeout-s <seconds>`: override connect timeout
- `--read-timeout-s <seconds>`: override read timeout
- `--timeout-profile default|slow`: timeout profile for vendor-slow endpoints (default: auto)
- `--cache-ttl-s <seconds>`: short-TTL cache for safe GET reads (default: 60)
- `--no-cache`: disable short-TTL caching
- `--parallel <N>`: max parallelism for batch read helpers (default: 1)

## Operations coverage source

- `cloudflare-api-tool operations <area> <op_key>` is generated from the committed live official Cloudflare API inventory.
- Active runtime allowlist: `docs/_generated/live_official_api_inventory.json`
- Human ledger: `docs/api_coverage_live_official.md`
- No generic raw-call bridge exists in this tool.

## Current before-state rule

- Dangerous `operations <area> <op_key>` writes now save live before-state when possible when a safe read path exists.
- `operations` writes that cannot save before-state require explicit no-snapshot approval for live apply.
- Named remote-write helpers below are currently dry-run-only unless they are local-only or read-like file-output commands. If a named write helper below shows an `--apply --yes` example, the command requires explicit no-snapshot approval until that helper gets saved before-state support.
- Read-like file-output helpers still apply with `--apply --out`, for example Browser Run, audit/log reads, D1 export, Queue pull, Workers code/KV/log reads, and request tracer.

## Config (local-only)

- `cloudflare-api-tool config init [--force] [--env-example <PATH>]`
- `cloudflare-api-tool config check`

## Onboarding

- `cloudflare-api-tool onboarding [--no-write-env]`

## Auth

- `cloudflare-api-tool --output json --version`
- `cloudflare-api-tool auth check`
- `cloudflare-api-tool auth probe [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool auth zone-create-check [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool auth doctor [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool auth explain --for observability speed page trend`

## Browser Run

Safety notes:
- Browser Run quick actions are account-scoped Browser Rendering requests.
- `markdown`, `links`, `scrape`, `screenshot`, `crawl`, and `crawl-result` are read-like file-output commands.
- Apply with `--apply --out ./file.json`; `--yes` is accepted but not required.
- Use `accounts set-default` once or pass `--account-id <ACCOUNT_ID>` on each command.

Common commands:
- `cloudflare-api-tool browser-run markdown [--account-id <ACCOUNT_ID>] (--url <URL> | --html <HTML>) --out ./markdown.json`
- `cloudflare-api-tool browser-run links [--account-id <ACCOUNT_ID>] (--url <URL> | --html <HTML>) --out ./links.json`
- `cloudflare-api-tool browser-run scrape [--account-id <ACCOUNT_ID>] (--url <URL> | --html <HTML>) --selector <CSS> [--selector <CSS> ...] --out ./scrape.json`
- `cloudflare-api-tool browser-run screenshot [--account-id <ACCOUNT_ID>] (--url <URL> | --html <HTML>) --out ./shot.bin`
- `cloudflare-api-tool browser-run crawl [--account-id <ACCOUNT_ID>] --url <URL> --out ./crawl_start.json`
- `cloudflare-api-tool browser-run crawl-result [--account-id <ACCOUNT_ID>] --job-id <JOB_ID> --out ./crawl_result.json`

Useful page-load flags:
- `--cache-ttl <SECONDS>`
- `--goto-timeout-ms <MS>`
- `--goto-wait-until <MODE>`
- `--wait-for-timeout-ms <MS>`
- `--wait-for-selector <CSS>`
- `--wait-for-selector-timeout-ms <MS>`
- `--wait-for-selector-visible`
- `--reject-resource-type <TYPE>` (repeatable)
- `--viewport-width <PX> --viewport-height <PX>`

Useful action-specific flags:
- `links`: `--visible-links-only`, `--exclude-external-links`
- `screenshot`: `--full-page`, `--omit-background`, `--image-type png|jpeg|webp`
- `crawl`: `--depth <N>` (must be `>= 1`), `--limit <N>`, `--source links|sitemaps`, `--format <FMT>`, `--include-pattern <PATTERN>`, `--exclude-pattern <PATTERN>`, `--include-subdomains`, `--include-external-links`, `--no-render`
- `crawl-result`: `--status <STATUS>`, `--limit <N>`, `--cursor <CURSOR>`

Examples:
- `cloudflare-api-tool --project-dir . --apply browser-run markdown --account-id <ACCOUNT_ID> --url https://example.com/ --out ./markdown.json`
- `cloudflare-api-tool --project-dir . --apply browser-run screenshot --account-id <ACCOUNT_ID> --url https://example.com/ --full-page --out ./shot.bin`
- `cloudflare-api-tool --project-dir . --apply browser-run crawl --account-id <ACCOUNT_ID> --url https://example.com/ --limit 10 --depth 1 --out ./crawl_start.json`
- `cloudflare-api-tool --project-dir . --apply browser-run crawl-result --account-id <ACCOUNT_ID> --job-id <JOB_ID> --out ./crawl_result.json`

## Accounts

- `cloudflare-api-tool accounts list [--page N] [--per-page N]`
- `cloudflare-api-tool accounts set-default --account-id <ACCOUNT_ID>`
- Roles:
  - `cloudflare-api-tool accounts roles list [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool accounts roles get --role-id <ROLE_ID> [--account-id <ACCOUNT_ID>]`
- Members (PII-safe; never printed; file-only):
  - Safety note: member `--out` JSON files can contain emails/PII; keep them local and never commit them.
  - `cloudflare-api-tool --project-dir . --output json --apply accounts members list --out ./account_members.json [--account-id <ACCOUNT_ID>] [--status accepted|pending]`
  - `cloudflare-api-tool --project-dir . --output json --apply accounts members get --member-id <MEMBER_ID> --out ./account_member.json [--account-id <ACCOUNT_ID>]`
  - Add (dry-run plan by default; apply with `--apply --yes`):
    - `cloudflare-api-tool --output json accounts members add --email <email> --role-id <ROLE_ID> [--role-id <ROLE_ID> ...] [--status pending|accepted] [--account-id <ACCOUNT_ID>]`
    - `cloudflare-api-tool --output json --apply --yes accounts members add --email <email> --role-id <ROLE_ID> [--role-id <ROLE_ID> ...] [--status pending|accepted] [--account-id <ACCOUNT_ID>]`
  - Update (dry-run plan by default; apply with `--apply --yes`):
    - `cloudflare-api-tool --output json accounts members update --member-id <MEMBER_ID> [--role-id <ROLE_ID> ...] [--status pending|accepted] [--account-id <ACCOUNT_ID>]`
    - `cloudflare-api-tool --output json --apply --yes accounts members update --member-id <MEMBER_ID> [--role-id <ROLE_ID> ...] [--status pending|accepted] [--account-id <ACCOUNT_ID>]`
  - Remove (dry-run plan by default; apply with `--apply --yes`):
    - `cloudflare-api-tool --output json accounts members remove --member-id <MEMBER_ID> [--account-id <ACCOUNT_ID>]`
    - `cloudflare-api-tool --output json --apply --yes accounts members remove --member-id <MEMBER_ID> [--account-id <ACCOUNT_ID>]`

## Zones

- `cloudflare-api-tool zones list [--name <ZONE>] [--account-id <ACCOUNT_ID>] [--status <STATUS>] [--page N] [--per-page N]`
- `cloudflare-api-tool zones resolve --name <ZONE> [--account-id <ACCOUNT_ID>]`

Zone settings (allowlisted; safe-by-default):
- `cloudflare-api-tool zones settings list --zone-id <ZONE_ID>`
- `cloudflare-api-tool zones settings patch --zone-id <ZONE_ID> --body-json-file <FILE>` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool zones settings setting-get --zone-id <ZONE_ID> --setting-path <SETTING>`
- `cloudflare-api-tool zones settings setting-patch --zone-id <ZONE_ID> --setting-path <SETTING> --body-json-file <FILE>` (dry-run by default; apply with `--apply --yes`)

Note: `--setting-path` is validated against the tool's generated allowlist (`src/cloudflare_api_tool/zone_settings_allowlist.py`).

## Observability (Logpush + Audit Logs + Request Tracer + Observatory speed + RUM/Web Analytics)

Logpush (account-scoped; sensitive; file-only output):
- `cloudflare-api-tool --project-dir . --apply observability logpush account datasets fields --dataset-id <DATASET_ID> --out ./dataset_fields.json [--account-id <ACCOUNT_ID>] [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply observability logpush account datasets jobs --dataset-id <DATASET_ID> --out ./dataset_jobs.json [--account-id <ACCOUNT_ID>] [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply observability logpush account jobs list --out ./logpush_jobs.json [--account-id <ACCOUNT_ID>] [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply observability logpush account jobs get --job-id <JOB_ID> --out ./logpush_job.json [--account-id <ACCOUNT_ID>] [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account jobs create --body-json-file ./body.json --out ./logpush_job_create.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account jobs update --job-id <JOB_ID> --body-json-file ./body.json --out ./logpush_job_update.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account jobs delete --job-id <JOB_ID> --out ./logpush_job_delete.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account ownership challenge --body-json-file ./body.json --out ./logpush_ownership_challenge.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account ownership validate --body-json-file ./body.json --out ./logpush_ownership_validate.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account validate destination --body-json-file ./body.json --out ./logpush_validate_destination.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account validate destination-exists --body-json-file ./body.json --out ./logpush_validate_destination_exists.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush account validate origin --body-json-file ./body.json --out ./logpush_validate_origin.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)

Logpush (zone-scoped + Instant Logs jobs; sensitive; file-only output):
- `cloudflare-api-tool --project-dir . --apply observability logpush zone datasets fields --zone-id <ZONE_ID> --dataset-id <DATASET_ID> --out ./dataset_fields.json [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply observability logpush zone datasets jobs --zone-id <ZONE_ID> --dataset-id <DATASET_ID> --out ./dataset_jobs.json [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply observability logpush zone jobs list --zone-id <ZONE_ID> --out ./logpush_jobs.json [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply observability logpush zone jobs get --zone-id <ZONE_ID> --job-id <JOB_ID> --out ./logpush_job.json [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone jobs create --zone-id <ZONE_ID> --body-json-file ./body.json --out ./logpush_job_create.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone jobs update --zone-id <ZONE_ID> --job-id <JOB_ID> --body-json-file ./body.json --out ./logpush_job_update.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone jobs delete --zone-id <ZONE_ID> --job-id <JOB_ID> --out ./logpush_job_delete.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply observability logpush zone instant-jobs list --zone-id <ZONE_ID> --out ./instant_jobs.json [--query k=v ...]`
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone instant-jobs create --zone-id <ZONE_ID> --body-json-file ./body.json --out ./instant_job_create.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone ownership challenge --zone-id <ZONE_ID> --body-json-file ./body.json --out ./logpush_ownership_challenge.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone ownership validate --zone-id <ZONE_ID> --body-json-file ./body.json --out ./logpush_ownership_validate.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone validate destination --zone-id <ZONE_ID> --body-json-file ./body.json --out ./logpush_validate_destination.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone validate destination-exists --zone-id <ZONE_ID> --body-json-file ./body.json --out ./logpush_validate_destination_exists.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool --project-dir . --apply --yes observability logpush zone validate origin --zone-id <ZONE_ID> --body-json-file ./body.json --out ./logpush_validate_origin.json` (dry-run by default; apply with `--apply --yes`)

Zone logs (sensitive; file-only):
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability logs received --zone-id <ZONE_ID> --out ./logs_received.json [--query k=v ...]`
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability logs received-fields --zone-id <ZONE_ID> --out ./logs_fields.json [--query k=v ...]`
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability logs rayid --zone-id <ZONE_ID> --ray-id <RAY_ID> --out ./logs_rayid.json [--query k=v ...]`

Audit logs (sensitive; file-only):
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability audit-logs account list [--account-id <ACCOUNT_ID>] --out ./account_audit.json [--query k=v ...]`
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability audit-logs account list-v2 [--account-id <ACCOUNT_ID>] --out ./account_audit_v2.json [--query k=v ...]`
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability audit-logs user list --out ./user_audit.json [--query k=v ...]`

Logs control (CMB config):
- `cloudflare-api-tool observability logs-control cmb get [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool observability logs-control cmb update --body-json-file ./body.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool observability logs-control cmb delete [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)

Request Tracer (read-like POST; sensitive; file-only):
- `cloudflare-api-tool --env-file .env --project-dir . --output json --apply observability request-tracer trace --body-json-file ./body.json --out ./trace.json [--account-id <ACCOUNT_ID>]` (no `--yes`)

Observatory speed (read-only summaries):
- `cloudflare-api-tool observability speed availabilities --zone-id <ZONE_ID>`
- `cloudflare-api-tool observability speed pages list --zone-id <ZONE_ID>`
- `cloudflare-api-tool observability speed page latest --zone-id <ZONE_ID> --url https://example.com/`
- `cloudflare-api-tool observability speed page trend --zone-id <ZONE_ID> --url https://example.com/`
- `cloudflare-api-tool observability speed page history --zone-id <ZONE_ID> --url https://example.com/`

These commands accept a normal URL and normalize it to Cloudflare’s internal Observatory page identifier automatically.

RUM / Web Analytics:
- Sites:
  - `cloudflare-api-tool observability rum sites list [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool observability rum sites create --body-json-file ./body.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool observability rum sites get --site-id <SITE_ID> [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool observability rum sites update --site-id <SITE_ID> --body-json-file ./body.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool observability rum sites delete --site-id <SITE_ID> [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- Rules:
  - `cloudflare-api-tool observability rum rules list --ruleset-id <RULESET_ID> [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool observability rum rules bulk-update --ruleset-id <RULESET_ID> --body-json-file ./body.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool observability rum rules create --ruleset-id <RULESET_ID> --body-json-file ./body.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool observability rum rules update --ruleset-id <RULESET_ID> --rule-id <RULE_ID> --body-json-file ./body.json [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool observability rum rules delete --ruleset-id <RULESET_ID> --rule-id <RULE_ID> [--account-id <ACCOUNT_ID>]` (dry-run by default; apply with `--apply --yes`)
- Zone RUM status:
  - `cloudflare-api-tool observability rum zone-settings get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool observability rum zone-settings toggle --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)

Web Analytics / RUM summary:
- `cloudflare-api-tool observability web-analytics status --zone-id <ZONE_ID> [--account-id <ACCOUNT_ID>]`

This status check separates "site lookup worked" from "site matched", so auth failures and no-match cases are easier to tell apart.

Bundled observability audit:
- `cloudflare-api-tool observability audit --zone-id <ZONE_ID> [--account-id <ACCOUNT_ID>] [--url https://example.com/]`

This bundles:
- zone RUM status
- matching Web Analytics site state
- Observatory availability + tested pages
- homepage/page performance summary
- Cloudflare log surface access status

## DNS (records + scans)

DNS records (zone-scoped):
- `cloudflare-api-tool dns records list --zone-id <ZONE_ID> [--name <NAME>] [--type <TYPE>] [--content <VALUE>] [--page N] [--per-page N]`
- `cloudflare-api-tool dns records get --zone-id <ZONE_ID> --record-id <RECORD_ID>`
- `cloudflare-api-tool dns records ensure --zone-id <ZONE_ID> --name <NAME> --type <TYPE> --content <VALUE>` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool dns records ensure-absent --zone-id <ZONE_ID> [--record-id <RECORD_ID>] [--name <NAME> --type <TYPE> --content <VALUE>]` (dry-run by default; apply with `--apply --yes`)

Sensitive export (file-only):
- `cloudflare-api-tool --project-dir . --apply dns records export --zone-id <ZONE_ID> --out ./dns_export.txt`

Bulk import (high risk):
- `cloudflare-api-tool --apply --yes --ack-irreversible dns records import --zone-id <ZONE_ID> --file ./dns_import.txt`

DNS scan (high risk; plan-first):
- `cloudflare-api-tool dns scan trigger --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes --ack-irreversible`)
- `cloudflare-api-tool dns scan review --zone-id <ZONE_ID>`
- `cloudflare-api-tool dns scan apply --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes --ack-irreversible`)

DNS settings (account + zone) and Internal DNS views:
- Zone settings:
  - `cloudflare-api-tool dns settings zone get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool dns settings zone update --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
- Account settings:
  - `cloudflare-api-tool dns settings account get [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool dns settings account update [--account-id <ACCOUNT_ID>] --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
- Internal DNS views:
  - `cloudflare-api-tool dns settings views list [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool dns settings views get [--account-id <ACCOUNT_ID>] --view-id <VIEW_ID>`
  - `cloudflare-api-tool dns settings views create [--account-id <ACCOUNT_ID>] --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns settings views update [--account-id <ACCOUNT_ID>] --view-id <VIEW_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns settings views delete [--account-id <ACCOUNT_ID>] --view-id <VIEW_ID>` (dry-run by default; apply with `--apply --yes`)

DNSSEC:
- `cloudflare-api-tool dns dnssec get --zone-id <ZONE_ID>`
- `cloudflare-api-tool dns dnssec set --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool dns dnssec delete --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)

Secondary DNS (ACL/Peer/TSIG + zone transfers):
- Account-scoped ACLs:
  - `cloudflare-api-tool dns secondary account acls list [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool dns secondary account acls get [--account-id <ACCOUNT_ID>] --acl-id <ACL_ID>`
  - `cloudflare-api-tool dns secondary account acls create [--account-id <ACCOUNT_ID>] --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary account acls update [--account-id <ACCOUNT_ID>] --acl-id <ACL_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary account acls delete [--account-id <ACCOUNT_ID>] --acl-id <ACL_ID>` (dry-run by default; apply with `--apply --yes`)
- Account-scoped peers:
  - `cloudflare-api-tool dns secondary account peers list [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool dns secondary account peers get [--account-id <ACCOUNT_ID>] --peer-id <PEER_ID>`
  - `cloudflare-api-tool dns secondary account peers create [--account-id <ACCOUNT_ID>] --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary account peers update [--account-id <ACCOUNT_ID>] --peer-id <PEER_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary account peers delete [--account-id <ACCOUNT_ID>] --peer-id <PEER_ID>` (dry-run by default; apply with `--apply --yes`)
- Account-scoped TSIGs (secret-bearing; file-only):
  - `cloudflare-api-tool --project-dir . --apply dns secondary account tsigs list [--account-id <ACCOUNT_ID>] --out ./tsigs.json`
  - `cloudflare-api-tool --project-dir . --apply dns secondary account tsigs get [--account-id <ACCOUNT_ID>] --tsig-id <TSIG_ID> --out ./tsig.json`
  - `cloudflare-api-tool --project-dir . --apply --yes --ack-irreversible dns secondary account tsigs create [--account-id <ACCOUNT_ID>] --body-json-file ./body.json --out ./tsig_create.json`
  - `cloudflare-api-tool --project-dir . --apply --yes --ack-irreversible dns secondary account tsigs update [--account-id <ACCOUNT_ID>] --tsig-id <TSIG_ID> --body-json-file ./body.json --out ./tsig_update.json`
  - `cloudflare-api-tool dns secondary account tsigs delete [--account-id <ACCOUNT_ID>] --tsig-id <TSIG_ID>` (dry-run by default; apply with `--apply --yes`)
- Zone transfers:
  - `cloudflare-api-tool dns secondary zone incoming get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool dns secondary zone incoming create --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone incoming update --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone incoming delete --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone outgoing get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool dns secondary zone outgoing create --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone outgoing update --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone outgoing delete --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone outgoing status --zone-id <ZONE_ID>`
  - `cloudflare-api-tool dns secondary zone outgoing enable --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone outgoing disable --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone outgoing force-notify --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)
  - `cloudflare-api-tool dns secondary zone force-axfr --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes`)

## TLS/SSL (Custom Hostnames + SSL/TLS + Cache purge)

Custom Hostnames (SSL for SaaS; sensitive file-only output):
- List (dry-run plan):
  - `cloudflare-api-tool custom-hostnames list --zone-id <ZONE_ID>`
- Apply (writes response to file; never prints):
  - `cloudflare-api-tool --project-dir . --apply custom-hostnames list --zone-id <ZONE_ID> --out ./custom_hostnames.json`
- Create/update/delete (write; sensitive output):
  - `cloudflare-api-tool custom-hostnames create --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./create.json`)
  - `cloudflare-api-tool custom-hostnames update --zone-id <ZONE_ID> --custom-hostname-id <ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./update.json`)
  - `cloudflare-api-tool custom-hostnames delete --zone-id <ZONE_ID> --custom-hostname-id <ID>` (dry-run by default; apply with `--apply --yes --out ./delete.json`)
- Fallback origin:
  - `cloudflare-api-tool custom-hostnames fallback-origin get --zone-id <ZONE_ID>` (apply with `--apply --out ./fallback_origin.json`)
  - `cloudflare-api-tool custom-hostnames fallback-origin update --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./fallback_origin_update.json`)
  - `cloudflare-api-tool custom-hostnames fallback-origin delete --zone-id <ZONE_ID>` (dry-run by default; apply with `--apply --yes --out ./fallback_origin_delete.json`)

SSL/TLS (sensitive file-only output):
- Automatic mode:
  - `cloudflare-api-tool ssl-tls automatic-mode get --zone-id <ZONE_ID>` (apply with `--apply --out ./automatic_mode.json`)
  - `cloudflare-api-tool ssl-tls automatic-mode set --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./automatic_mode_set.json`)
- Analyze certificate (read-like POST; no `--yes`):
  - `cloudflare-api-tool ssl-tls analyze --zone-id <ZONE_ID>` (apply with `--apply --out ./analyze.json`)
- Recommendation:
  - `cloudflare-api-tool ssl-tls recommendation --zone-id <ZONE_ID>` (apply with `--apply --out ./recommendation.json`)
- Universal SSL settings:
  - `cloudflare-api-tool ssl-tls universal-ssl get --zone-id <ZONE_ID>` (apply with `--apply --out ./universal_ssl.json`)
  - `cloudflare-api-tool ssl-tls universal-ssl set --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./universal_ssl_set.json`)
- Verification:
  - `cloudflare-api-tool ssl-tls verification get --zone-id <ZONE_ID>` (apply with `--apply --out ./verification.json`)
  - `cloudflare-api-tool ssl-tls verification update --zone-id <ZONE_ID> --certificate-pack-id <PACK_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./verification_update.json`)
- Certificate packs:
  - `cloudflare-api-tool ssl-tls certificate-packs list --zone-id <ZONE_ID>` (apply with `--apply --out ./certificate_packs.json`)
  - `cloudflare-api-tool ssl-tls certificate-packs get --zone-id <ZONE_ID> --certificate-pack-id <PACK_ID>` (apply with `--apply --out ./certificate_pack.json`)
  - `cloudflare-api-tool ssl-tls certificate-packs quota --zone-id <ZONE_ID>` (apply with `--apply --out ./certificate_packs_quota.json`)
  - `cloudflare-api-tool ssl-tls certificate-packs order --zone-id <ZONE_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./certificate_packs_order.json`)
  - `cloudflare-api-tool ssl-tls certificate-packs update --zone-id <ZONE_ID> --certificate-pack-id <PACK_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./certificate_packs_update.json`)
  - `cloudflare-api-tool ssl-tls certificate-packs restart --zone-id <ZONE_ID> --certificate-pack-id <PACK_ID> --body-json-file ./body.json` (dry-run by default; apply with `--apply --yes --out ./certificate_packs_restart.json`)
  - `cloudflare-api-tool ssl-tls certificate-packs delete --zone-id <ZONE_ID> --certificate-pack-id <PACK_ID>` (dry-run by default; apply with `--apply --yes --out ./certificate_packs_delete.json`)

Cache purge (write; dry-run plan by default):
- `cloudflare-api-tool cache purge --zone-id <ZONE_ID> --body-json-file ./purge.json`
- Apply (requires explicit confirmation):
  - `cloudflare-api-tool --apply --yes cache purge --zone-id <ZONE_ID> --body-json-file ./purge.json`

Load Balancers (Phase 7E-2; sensitive file-only output):
- Monitors:
  - `cloudflare-api-tool load-balancers monitors list --account-id <ACCOUNT_ID>` (apply with `--apply --out ./monitors.json`)
  - `cloudflare-api-tool load-balancers monitors get --account-id <ACCOUNT_ID> --monitor-id <MONITOR_ID>` (apply with `--apply --out ./monitor.json`)
  - `cloudflare-api-tool load-balancers monitors references --account-id <ACCOUNT_ID> --monitor-id <MONITOR_ID>` (apply with `--apply --out ./monitor_refs.json`)
  - `cloudflare-api-tool load-balancers monitors preview --account-id <ACCOUNT_ID> --monitor-id <MONITOR_ID> [--body-json-file ./body.json]` (read-like POST; apply with `--apply --out ./monitor_preview.json`; no `--yes`)
  - Writes (dry-run by default; apply requires explicit confirmation):
    - `cloudflare-api-tool load-balancers monitors create --account-id <ACCOUNT_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./monitor_create.json`)
    - `cloudflare-api-tool load-balancers monitors update --account-id <ACCOUNT_ID> --monitor-id <MONITOR_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./monitor_update.json`)
    - `cloudflare-api-tool load-balancers monitors patch --account-id <ACCOUNT_ID> --monitor-id <MONITOR_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./monitor_patch.json`)
    - `cloudflare-api-tool load-balancers monitors delete --account-id <ACCOUNT_ID> --monitor-id <MONITOR_ID>` (apply with `--apply --yes --out ./monitor_delete.json`)
- Pools:
  - `cloudflare-api-tool load-balancers pools list --account-id <ACCOUNT_ID>` (apply with `--apply --out ./pools.json`)
  - `cloudflare-api-tool load-balancers pools get --account-id <ACCOUNT_ID> --pool-id <POOL_ID>` (apply with `--apply --out ./pool.json`)
  - `cloudflare-api-tool load-balancers pools health --account-id <ACCOUNT_ID> --pool-id <POOL_ID>` (apply with `--apply --out ./pool_health.json`)
  - `cloudflare-api-tool load-balancers pools references --account-id <ACCOUNT_ID> --pool-id <POOL_ID>` (apply with `--apply --out ./pool_refs.json`)
  - `cloudflare-api-tool load-balancers pools preview --account-id <ACCOUNT_ID> --pool-id <POOL_ID> [--body-json-file ./body.json]` (read-like POST; apply with `--apply --out ./pool_preview.json`; no `--yes`)
  - Writes (dry-run by default; apply requires explicit confirmation):
    - `cloudflare-api-tool load-balancers pools create --account-id <ACCOUNT_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./pool_create.json`)
    - `cloudflare-api-tool load-balancers pools update --account-id <ACCOUNT_ID> --pool-id <POOL_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./pool_update.json`)
    - `cloudflare-api-tool load-balancers pools patch --account-id <ACCOUNT_ID> --pool-id <POOL_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./pool_patch.json`)
    - `cloudflare-api-tool load-balancers pools patch-all --account-id <ACCOUNT_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./pool_patch_all.json`)
    - `cloudflare-api-tool load-balancers pools delete --account-id <ACCOUNT_ID> --pool-id <POOL_ID>` (apply with `--apply --yes --out ./pool_delete.json`)
- Monitor groups:
  - `cloudflare-api-tool load-balancers monitor-groups list --account-id <ACCOUNT_ID>` (apply with `--apply --out ./monitor_groups.json`)
  - `cloudflare-api-tool load-balancers monitor-groups get --account-id <ACCOUNT_ID> --monitor-group-id <GROUP_ID>` (apply with `--apply --out ./monitor_group.json`)
  - `cloudflare-api-tool load-balancers monitor-groups references --account-id <ACCOUNT_ID> --monitor-group-id <GROUP_ID>` (apply with `--apply --out ./monitor_group_refs.json`)
  - Writes (dry-run by default; apply requires explicit confirmation):
    - `cloudflare-api-tool load-balancers monitor-groups create --account-id <ACCOUNT_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./monitor_group_create.json`)
    - `cloudflare-api-tool load-balancers monitor-groups update --account-id <ACCOUNT_ID> --monitor-group-id <GROUP_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./monitor_group_update.json`)
    - `cloudflare-api-tool load-balancers monitor-groups patch --account-id <ACCOUNT_ID> --monitor-group-id <GROUP_ID> --body-json-file ./body.json` (apply with `--apply --yes --out ./monitor_group_patch.json`)
    - `cloudflare-api-tool load-balancers monitor-groups delete --account-id <ACCOUNT_ID> --monitor-group-id <GROUP_ID>` (apply with `--apply --yes --out ./monitor_group_delete.json`)

- Regions:
  - `cloudflare-api-tool load-balancers regions list --account-id <ACCOUNT_ID>` (apply with `--apply --out ./lb_regions.json`)
  - `cloudflare-api-tool load-balancers regions get --account-id <ACCOUNT_ID> --region-id <REGION_ID>` (apply with `--apply --out ./lb_region.json`)

- Search:
  - `cloudflare-api-tool load-balancers search --account-id <ACCOUNT_ID> [--query k=v ...]` (apply with `--apply --out ./lb_search.json`)

- Preview results:
  - `cloudflare-api-tool load-balancers preview-result get --account-id <ACCOUNT_ID> --preview-id <PREVIEW_ID>` (apply with `--apply --out ./lb_preview_result.json`)

## Registrar (domains)

Registrar domain objects can include registrant PII. This tool treats all Registrar endpoints as sensitive output:
- Dry-run prints a plan only (no API calls).
- Apply writes the raw response bytes to `--out` under `--project-dir`.
- Response bodies are never printed to stdout/stderr.

Dry-run (plan only):
- `cloudflare-api-tool registrar domains list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool registrar domains get --domain-name <DOMAIN> [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool registrar domains update --domain-name <DOMAIN> --body-json-file ./body.json [--account-id <ACCOUNT_ID>]`

Apply (file-only output; never prints):
- List/get (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply registrar domains list --out ./domains.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool --project-dir . --apply registrar domains get --domain-name <DOMAIN> --out ./domain.json [--account-id <ACCOUNT_ID>]`
- Update (write; requires explicit confirmation):
  - `cloudflare-api-tool --project-dir . --apply --yes registrar domains update --domain-name <DOMAIN> --body-json-file ./body.json --out ./domain_update.json [--account-id <ACCOUNT_ID>]`

## Turnstile (widgets)

Turnstile widget configuration is treated as sensitive output:
- Dry-run prints a plan only (no API calls).
- Apply writes the raw response bytes to `--out` under `--project-dir`.
- Response bodies are never printed to stdout/stderr.
- Secret-bearing operations require `--ack-irreversible`.

Dry-run (plan only):
- `cloudflare-api-tool turnstile widgets list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool turnstile widgets get --sitekey <SITEKEY> [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool turnstile widgets create --body-json-file ./body.json [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool turnstile widgets update --sitekey <SITEKEY> --body-json-file ./body.json [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool turnstile widgets delete --sitekey <SITEKEY> [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool turnstile widgets rotate-secret --sitekey <SITEKEY> [--account-id <ACCOUNT_ID>]`

Apply (file-only output; never prints):
- List/get (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply turnstile widgets list --out ./turnstile_widgets.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool --project-dir . --apply turnstile widgets get --sitekey <SITEKEY> --out ./turnstile_widget.json [--account-id <ACCOUNT_ID>]`
- Update/delete (write; requires explicit confirmation):
  - `cloudflare-api-tool --project-dir . --apply --yes turnstile widgets update --sitekey <SITEKEY> --body-json-file ./body.json --out ./turnstile_widget_update.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool --project-dir . --apply --yes turnstile widgets delete --sitekey <SITEKEY> --out ./turnstile_widget_delete.json [--account-id <ACCOUNT_ID>]`
- Create/rotate-secret (secret-bearing; requires `--ack-irreversible`):
  - `cloudflare-api-tool --project-dir . --apply --yes --ack-irreversible turnstile widgets create --body-json-file ./body.json --out ./turnstile_widget_create.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool --project-dir . --apply --yes --ack-irreversible turnstile widgets rotate-secret --sitekey <SITEKEY> --out ./turnstile_widget_rotated.json [--account-id <ACCOUNT_ID>]`

## Email Routing (addresses + settings + DNS + rules)

Email Routing data contains destination addresses and rule patterns (PII). This tool treats all Email Routing endpoints as sensitive output:
- Dry-run prints a plan only (no API calls).
- Apply writes the raw response bytes to `--out` under `--project-dir`.
- Response bodies are never printed to stdout/stderr.

Dry-run (plan only):
- Addresses (account-scoped):
  - `cloudflare-api-tool email-routing addresses list [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool email-routing addresses get --destination-address-identifier <ID> [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool email-routing addresses create --body-json-file ./body.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool email-routing addresses delete --destination-address-identifier <ID> [--account-id <ACCOUNT_ID>]`
- Settings (zone-scoped):
  - `cloudflare-api-tool email-routing settings get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing settings enable --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing settings disable --zone-id <ZONE_ID>`
- DNS (zone-scoped):
  - `cloudflare-api-tool email-routing dns get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing dns enable --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing dns disable --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing dns unlock --zone-id <ZONE_ID>`
- Rules (zone-scoped):
  - `cloudflare-api-tool email-routing rules list --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing rules get --zone-id <ZONE_ID> --rule-identifier <ID>`
  - `cloudflare-api-tool email-routing rules create --zone-id <ZONE_ID> --body-json-file ./body.json`
  - `cloudflare-api-tool email-routing rules update --zone-id <ZONE_ID> --rule-identifier <ID> --body-json-file ./body.json`
  - `cloudflare-api-tool email-routing rules delete --zone-id <ZONE_ID> --rule-identifier <ID>`
  - `cloudflare-api-tool email-routing rules catch-all get --zone-id <ZONE_ID>`
  - `cloudflare-api-tool email-routing rules catch-all update --zone-id <ZONE_ID> --body-json-file ./body.json`

Apply (file-only output; never prints):
- Reads (no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply email-routing addresses list --out ./email_routing_addresses.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool --project-dir . --apply email-routing settings get --zone-id <ZONE_ID> --out ./email_routing_settings.json`
  - `cloudflare-api-tool --project-dir . --apply email-routing dns get --zone-id <ZONE_ID> --out ./email_routing_dns.json`
  - `cloudflare-api-tool --project-dir . --apply email-routing rules list --zone-id <ZONE_ID> --out ./email_routing_rules.json`
- Writes (requires explicit confirmation):
  - `cloudflare-api-tool --project-dir . --apply --yes email-routing addresses create --body-json-file ./body.json --out ./email_routing_address_create.json [--account-id <ACCOUNT_ID>]`
  - `cloudflare-api-tool --project-dir . --apply --yes email-routing settings enable --zone-id <ZONE_ID> --out ./email_routing_settings_enable.json`
  - `cloudflare-api-tool --project-dir . --apply --yes email-routing dns enable --zone-id <ZONE_ID> --out ./email_routing_dns_enable.json`
  - `cloudflare-api-tool --project-dir . --apply --yes email-routing rules create --zone-id <ZONE_ID> --body-json-file ./body.json --out ./email_routing_rule_create.json`
  - `cloudflare-api-tool --project-dir . --apply --yes email-routing rules catch-all update --zone-id <ZONE_ID> --body-json-file ./body.json --out ./email_routing_catch_all_update.json`

## Email Security (Investigate + Settings + DLP Email + Radar Email)

Email Security endpoints can return raw email content, traces, detections, and other message metadata. Settings and DLP Email rules can include email addresses/domains/patterns. Radar Email endpoints are analytics, but are scoped to "User Details" (PII-risk).

This tool treats **all** Phase 16 Email Security endpoints as sensitive output:
- Dry-run prints a plan only (no API calls).
- Apply writes the raw response bytes to `--out` under `--project-dir`.
- Response bodies are never printed to stdout/stderr.
- Writes require `--apply --yes` and file output (`--out`).

Discovery (hidden-by-default):
- `cloudflare-api-tool operations list --contains email-security --limit 20`
- `cloudflare-api-tool operations list --contains email-security --limit 20 --include-sensitive`

Dry-run (plan only):
- Investigate search:
  - `cloudflare-api-tool operations email_security email-security-investigate --path-param account_id=<ACCOUNT_ID> --query q=from:example.com`
- Message raw/preview/trace:
  - `cloudflare-api-tool operations email_security email-security-get-message-raw --path-param account_id=<ACCOUNT_ID> --path-param postfix_id=<POSTFIX_ID>`
- Settings:
  - `cloudflare-api-tool operations email_security_settings email-security-list-allow-policies --path-param account_id=<ACCOUNT_ID>`
- DLP Email:
  - `cloudflare-api-tool operations dlp_email dlp-email-scanner-list-all-rules --path-param account_id=<ACCOUNT_ID>`
- Radar Email Security summary:
  - `cloudflare-api-tool operations radar_email_security radar-get-email-security-summary --path-param dimension=arc`

Apply (file-only output; never prints):
- Investigate search (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations email_security email-security-investigate --path-param account_id=<ACCOUNT_ID> --query q=from:example.com --out ./email_security_investigate.json`
- Message raw email content (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations email_security email-security-get-message-raw --path-param account_id=<ACCOUNT_ID> --path-param postfix_id=<POSTFIX_ID> --out ./email_raw.eml`
- Settings list (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations email_security_settings email-security-list-allow-policies --path-param account_id=<ACCOUNT_ID> --out ./email_security_allow_policies.json`
- DLP Email rules list (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations dlp_email dlp-email-scanner-list-all-rules --path-param account_id=<ACCOUNT_ID> --out ./dlp_email_rules.json`
- Radar Email Security summary (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_email_security radar-get-email-security-summary --path-param dimension=arc --out ./radar_email_security_summary_arc.json`

## Radar analytics (complete)

Radar endpoints are analytics, but are scoped to "User Details" token groups (PII-risk).

This tool treats ALL `/radar/*` operations as sensitive output:
- Dry-run prints a plan only (no API calls).
- Apply writes the raw response bytes to `--out` under `--project-dir`.
- Response bodies are never printed to stdout/stderr.
- Most reads (GET) do not require `--yes`, but do require file output (`--out`).
- Non-GET Radar operations require `--yes` and file output (`--out`).

Discovery (hidden-by-default):
- `cloudflare-api-tool operations list --contains /radar/ --limit 20`
- `cloudflare-api-tool operations list --contains /radar/ --limit 20 --include-sensitive`
- `cloudflare-api-tool operations list --contains /radar/http/ --limit 20`
- `cloudflare-api-tool operations list --contains /radar/http/ --limit 20 --include-sensitive`
- `cloudflare-api-tool operations list --contains /radar/dns/ --limit 20`
- `cloudflare-api-tool operations list --contains /radar/dns/ --limit 20 --include-sensitive`
- `cloudflare-api-tool operations list --contains /radar/bgp/ --limit 20`
- `cloudflare-api-tool operations list --contains /radar/bgp/ --limit 20 --include-sensitive`
- `cloudflare-api-tool operations list --contains /radar/netflows/ --limit 20`
- `cloudflare-api-tool operations list --contains /radar/netflows/ --limit 20 --include-sensitive`

Dry-run (plan only):
- Radar HTTP summary:
  - `cloudflare-api-tool operations radar_all radar-get-http-summary --path-param dimension=http_requests`
- Radar HTTP timeseries:
  - `cloudflare-api-tool operations radar_all radar-get-http-timeseries`
- Radar DNS summary:
  - `cloudflare-api-tool operations radar_all radar-get-dns-summary --path-param dimension=query_type`
- Radar DNS timeseries:
  - `cloudflare-api-tool operations radar_all radar-get-dns-timeseries`
- Radar BGP timeseries:
  - `cloudflare-api-tool operations radar_all radar-get-bgp-timeseries`
- Radar NetFlows timeseries:
  - `cloudflare-api-tool operations radar_all radar-get-netflows-timeseries`
- Radar dataset download URL (`POST /radar/datasets/download`) (plan only):
  - `cloudflare-api-tool operations radar_all radar-post-reports-dataset-download-url`

Apply (file-only output; never prints):
- Radar HTTP summary (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_all radar-get-http-summary --path-param dimension=http_requests --out ./radar_http_summary_http_requests.json`
- Radar HTTP timeseries (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_all radar-get-http-timeseries --out ./radar_http_timeseries.json`
- Radar DNS summary (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_all radar-get-dns-summary --path-param dimension=query_type --out ./radar_dns_summary_query_type.json`
- Radar DNS timeseries (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_all radar-get-dns-timeseries --out ./radar_dns_timeseries.json`
- Radar BGP timeseries (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_all radar-get-bgp-timeseries --out ./radar_bgp_timeseries.json`
- Radar NetFlows timeseries (read-only; no `--yes`):
  - `cloudflare-api-tool --project-dir . --apply operations radar_all radar-get-netflows-timeseries --out ./radar_netflows_timeseries.json`
- Radar dataset download URL (`POST /radar/datasets/download`) (non-GET; requires `--apply --yes --out`):
  - `cloudflare-api-tool --project-dir . --apply --yes operations radar_all radar-post-reports-dataset-download-url --out ./radar_datasets_download_url.json`

## WAF / Rulesets (inventory + safe writes + sensitive reads)

Rulesets (zone or account):
- `cloudflare-api-tool waf rulesets list --zone-id <ZONE_ID>`
- `cloudflare-api-tool waf rulesets list --account-id <ACCOUNT_ID>`
- `cloudflare-api-tool waf rulesets get --zone-id <ZONE_ID> --ruleset-id <RULESET_ID>`
- `cloudflare-api-tool waf rulesets get --account-id <ACCOUNT_ID> --ruleset-id <RULESET_ID>`
- `cloudflare-api-tool waf rulesets entrypoint-get --zone-id <ZONE_ID> --ruleset-phase <PHASE>`
- `cloudflare-api-tool waf rulesets entrypoint-update --zone-id <ZONE_ID> --ruleset-phase <PHASE> --body-json-file <FILE>` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool waf rulesets entrypoint-update --account-id <ACCOUNT_ID> --ruleset-phase <PHASE> --body-json-file <FILE>` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool waf rulesets versions-list --zone-id <ZONE_ID> --ruleset-id <RULESET_ID>`

Firewall access rules (choose exactly one scope):
- Zone scope:
  - `cloudflare-api-tool waf firewall access-rules list --zone-id <ZONE_ID>`
  - `cloudflare-api-tool waf firewall access-rules get --zone-id <ZONE_ID> --rule-id <RULE_ID>`
- Account scope:
  - `cloudflare-api-tool waf firewall access-rules list --account-id <ACCOUNT_ID>`
  - `cloudflare-api-tool waf firewall access-rules get --account-id <ACCOUNT_ID> --rule-id <RULE_ID>`
- User scope:
  - `cloudflare-api-tool waf firewall access-rules list --user`
  - `cloudflare-api-tool waf firewall access-rules get --user --rule-id <RULE_ID>`

Rate limits (zone-scoped):
- `cloudflare-api-tool waf rate-limits list --zone-id <ZONE_ID>`
- `cloudflare-api-tool waf rate-limits get --zone-id <ZONE_ID> --rate-limit-id <RATE_LIMIT_ID>`

Snippets (zone-scoped):
- `cloudflare-api-tool waf snippets list --zone-id <ZONE_ID>`
- `cloudflare-api-tool waf snippets get --zone-id <ZONE_ID> --snippet-name <NAME>`
Sensitive snippet content (file-only; never printed):
- `cloudflare-api-tool --project-dir . --apply waf snippets content get --zone-id <ZONE_ID> --snippet-name <NAME> --out ./snippet.txt`

Page rules (zone-scoped):
- `cloudflare-api-tool waf page-rules list --zone-id <ZONE_ID>`
- `cloudflare-api-tool waf page-rules get --zone-id <ZONE_ID> --pagerule-id <ID>`

Managed transforms (OpenAPI path: `/managed_headers`):
- `cloudflare-api-tool waf managed-transforms get --zone-id <ZONE_ID>`
Update (plan-first; apply requires `--apply --yes`):
- `cloudflare-api-tool waf managed-transforms update --zone-id <ZONE_ID> --body-json-file ./body.json`
- `cloudflare-api-tool --apply --yes waf managed-transforms update --zone-id <ZONE_ID> --body-json-file ./body.json`

## Workers platform (inventory + safe writes + sensitive reads)

Account-scoped commands accept `--account-id`. If omitted, the tool uses the local default set via
`accounts set-default`.

Scripts (metadata only):
- `cloudflare-api-tool workers scripts list [--account-id <ACCOUNT_ID>] [--tags "<TAGS>"]`
- `cloudflare-api-tool workers scripts search [--account-id <ACCOUNT_ID>] [--name "<NAME>"] [--page N] [--per-page N]`
- `cloudflare-api-tool workers scripts get [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers scripts schedules get [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers scripts script-settings get [--account-id <ACCOUNT_ID>] --script-name <NAME>`

Script observability (plan-first; applies via PATCH script-settings):
- `cloudflare-api-tool workers observability status [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers observability enable [--account-id <ACCOUNT_ID>] --script-name <NAME> [--head-sampling-rate 0.1]` (dry-run by default; apply with `--apply --yes`)
- `cloudflare-api-tool workers observability disable [--account-id <ACCOUNT_ID>] --script-name <NAME>` (dry-run by default; apply with `--apply --yes`)

- `cloudflare-api-tool workers scripts usage-model get [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers scripts subdomain get [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers scripts secrets list [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers scripts secrets get [--account-id <ACCOUNT_ID>] --script-name <NAME> --secret-name <NAME>`

Account settings (metadata only):
- `cloudflare-api-tool workers account-settings get [--account-id <ACCOUNT_ID>]`

Placement (metadata only):
- `cloudflare-api-tool workers placement regions list [--account-id <ACCOUNT_ID>]`

Workers for Platforms (inventory):
- `cloudflare-api-tool workers platforms list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers platforms get [--account-id <ACCOUNT_ID>] --worker-id <WORKER_ID>`

Services (metadata only):
- `cloudflare-api-tool workers services env settings get [--account-id <ACCOUNT_ID>] --service-name <NAME> --environment-name <NAME>`

Routes (zone-scoped):
- `cloudflare-api-tool workers routes list --zone-id <ZONE_ID>`
- `cloudflare-api-tool workers routes get --zone-id <ZONE_ID> --route-id <ROUTE_ID>`
- `cloudflare-api-tool workers routes ensure --zone-id <ZONE_ID> --pattern "<PATTERN>" --script-name <SCRIPT> [--apply --yes]`
- `cloudflare-api-tool workers routes ensure-absent --zone-id <ZONE_ID> --pattern "<PATTERN>" [--apply --yes]`

Subdomain:
- `cloudflare-api-tool workers subdomain get [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers subdomain ensure [--account-id <ACCOUNT_ID>] --subdomain <NAME> [--apply --yes]`
- `cloudflare-api-tool workers subdomain ensure-absent [--account-id <ACCOUNT_ID>] [--apply --yes]`

Domains:
- `cloudflare-api-tool workers domains list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers domains get [--account-id <ACCOUNT_ID>] --domain-id <DOMAIN_ID>`
- `cloudflare-api-tool workers domains attach [--account-id <ACCOUNT_ID>] --zone-id <ZONE_ID> --hostname <HOSTNAME> --service <SERVICE> [--environment <ENV>] [--apply --yes]`
- `cloudflare-api-tool workers domains detach [--account-id <ACCOUNT_ID>] --domain-id <DOMAIN_ID> [--apply --yes]`

Dispatch:
- `cloudflare-api-tool workers dispatch namespaces list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers dispatch namespaces get [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME>`
- `cloudflare-api-tool workers dispatch scripts list [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME>`
- `cloudflare-api-tool workers dispatch scripts get [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME> --script-name <NAME>`
- `cloudflare-api-tool workers dispatch scripts bindings list [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME> --script-name <NAME>`
- `cloudflare-api-tool workers dispatch scripts tags list [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME> --script-name <NAME>`
- `cloudflare-api-tool workers dispatch scripts secrets list [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME> --script-name <NAME>`
- `cloudflare-api-tool workers dispatch scripts secrets get [--account-id <ACCOUNT_ID>] --dispatch-namespace <NAME> --script-name <NAME> --secret-name <NAME>`

Builds:
- `cloudflare-api-tool workers builds list [--account-id <ACCOUNT_ID>] --external-script-id <ID>`
- `cloudflare-api-tool workers builds triggers list [--account-id <ACCOUNT_ID>] --external-script-id <ID>`

Pipelines:
- `cloudflare-api-tool workers pipelines list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers pipelines get [--account-id <ACCOUNT_ID>] --pipeline-id <ID>`
- `cloudflare-api-tool workers pipelines sinks list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers pipelines sinks get [--account-id <ACCOUNT_ID>] --sink-id <ID>`
- `cloudflare-api-tool workers pipelines streams list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers pipelines streams get [--account-id <ACCOUNT_ID>] --stream-id <ID>`
- `cloudflare-api-tool workers pipelines legacy list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers pipelines legacy get [--account-id <ACCOUNT_ID>] --pipeline-name <NAME>`

KV (metadata only; never values):
- `cloudflare-api-tool workers kv namespaces list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool workers kv namespaces get [--account-id <ACCOUNT_ID>] --namespace-id <NAMESPACE_ID>`
- `cloudflare-api-tool workers kv keys list [--account-id <ACCOUNT_ID>] --namespace-id <NAMESPACE_ID> [--limit N] [--prefix "<PREFIX>"] [--cursor "<CURSOR>"] [--all] [--max-rows N]`
- `cloudflare-api-tool workers kv keys metadata-get [--account-id <ACCOUNT_ID>] --namespace-id <NAMESPACE_ID> --key-name <KEY>`
KV values (sensitive; file output only):
- `cloudflare-api-tool workers kv values get [--account-id <ACCOUNT_ID>] --namespace-id <NAMESPACE_ID> --key-name <KEY> --out <FILE> [--overwrite] [--apply]`

Scripts (sensitive reads; file output only):
- `cloudflare-api-tool workers scripts download [--account-id <ACCOUNT_ID>] --script-name <NAME> --out <FILE> [--overwrite] [--apply]`
- `cloudflare-api-tool workers scripts content get [--account-id <ACCOUNT_ID>] --script-name <NAME> --out <FILE> [--overwrite] [--apply]`

Versions:
- `cloudflare-api-tool workers versions list [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers versions get [--account-id <ACCOUNT_ID>] --script-name <NAME> --version-id <VERSION_ID>`

Deployments:
- `cloudflare-api-tool workers deployments list [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers deployments get [--account-id <ACCOUNT_ID>] --script-name <NAME> --deployment-id <DEPLOYMENT_ID>`

Tails (listing + file-only streaming):
- `cloudflare-api-tool workers tails list [--account-id <ACCOUNT_ID>] --script-name <NAME>`
- `cloudflare-api-tool workers tails stream [--account-id <ACCOUNT_ID>] --script-name <NAME> --out <FILE> [--duration-s 60] [--overwrite]` (dry-run by default; apply with `--apply --yes`)

Safety note: tail events can contain PII; `workers tails stream` writes events only to the output file and never prints them.

Stored logs (Telemetry API; PII-risk; file-only output):
- `cloudflare-api-tool workers logs search [--account-id <ACCOUNT_ID>] --error-id <ERROR_ID> --out <FILE> [--script-name <NAME>] [--from <TIME>] [--to <TIME>] [--limit N] [--request-id-key <KEY>] [--dataset <DATASET> ...] [--overwrite]` (dry-run by default; apply with `--apply`)
- `cloudflare-api-tool workers logs keys [--account-id <ACCOUNT_ID>] --out <FILE> [--from <TIME>] [--to <TIME>] [--limit N] [--dataset <DATASET> ...] [--key-needle <TEXT>] [--needle <TEXT>] [--overwrite]` (dry-run by default; apply with `--apply`)
- `cloudflare-api-tool workers logs values [--account-id <ACCOUNT_ID>] --key <KEY> --type string|number|boolean --out <FILE> [--from <TIME>] [--to <TIME>] [--limit N] [--dataset <DATASET> ...] [--needle <TEXT>] [--overwrite]` (dry-run by default; apply with `--apply`)

Debug by Error ID (recommended flow):
1) Dry-run plan:
   - `cloudflare-api-tool workers logs search --error-id <ERROR_ID> --out ./telemetry_query.json`
2) Apply (writes Telemetry response to file; never prints payloads):
   - `cloudflare-api-tool --project-dir . --apply workers logs search --error-id <ERROR_ID> --out ./telemetry_query.json`
3) If the tool refuses (cannot discover the request-id key):
   - Run `cloudflare-api-tool --project-dir . --apply workers logs keys --out ./telemetry_keys.json`
   - Re-run search with `--request-id-key <KEY>`

## D1 (databases)

Databases:
- `cloudflare-api-tool d1 databases list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool d1 databases get [--account-id <ACCOUNT_ID>] --database-id <DATABASE_ID>`

Export (sensitive; file-only; read-like POST):
- `cloudflare-api-tool d1 export [--account-id <ACCOUNT_ID>] --database-id <DATABASE_ID> --out <FILE> [--overwrite] [--apply]`

Query (sensitive; file-only; SQL can be mutating):
- `cloudflare-api-tool d1 query [--account-id <ACCOUNT_ID>] --database-id <DATABASE_ID> --body-json-file <FILE> --out <FILE> [--overwrite] [--apply --yes]`

## Queues

- `cloudflare-api-tool queues list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool queues get [--account-id <ACCOUNT_ID>] --queue-id <QUEUE_ID>`
Pull messages (sensitive; file-only; read-like POST):
- `cloudflare-api-tool queues pull [--account-id <ACCOUNT_ID>] --queue-id <QUEUE_ID> --out <FILE> [--overwrite] [--apply]`

## R2

Buckets:
- `cloudflare-api-tool r2 buckets list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool r2 buckets get [--account-id <ACCOUNT_ID>] --bucket-name <BUCKET_NAME>`

Temp creds (secret-bearing; file-only):
- `cloudflare-api-tool r2 temp-creds create [--account-id <ACCOUNT_ID>] --bucket <BUCKET_NAME> --permission <PERMISSION> --ttl-seconds <N> --parent-access-key-id <ACCESS_KEY_ID> [--prefix <PREFIX> ...] [--object <OBJECT> ...] --out <FILE> [--overwrite] [--apply --yes --ack-irreversible]`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `cloudflare-api-tool runs list [--limit 20]`
- `cloudflare-api-tool runs show --run-id <RUN_ID>`

## Zero Trust (read-only inventory)

Organization:
- `cloudflare-api-tool zero-trust org get [--account-id <ACCOUNT_ID>]`

Gateway:
- `cloudflare-api-tool zero-trust gateway account get [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool zero-trust gateway configuration get [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool zero-trust gateway logging get [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool zero-trust gateway rules list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool zero-trust gateway rules get [--account-id <ACCOUNT_ID>] --rule-id <RULE_ID>`
- `cloudflare-api-tool zero-trust gateway lists list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool zero-trust gateway lists get [--account-id <ACCOUNT_ID>] --list-id <LIST_ID>`
- `cloudflare-api-tool zero-trust gateway lists items list [--account-id <ACCOUNT_ID>] --list-id <LIST_ID>`

Devices:
- `cloudflare-api-tool zero-trust devices list [--account-id <ACCOUNT_ID>]`
- `cloudflare-api-tool zero-trust devices get [--account-id <ACCOUNT_ID>] --device-id <DEVICE_ID>`

Access:
- `cloudflare-api-tool zero-trust access apps list [--account-id <ACCOUNT_ID>] [--search "<TEXT>"] [--exact]`
- `cloudflare-api-tool zero-trust access apps resolve [--account-id <ACCOUNT_ID>] [--name "<NAME>"] [--domain "<DOMAIN>"] [--aud "<AUD>"] [--exact]`
- `cloudflare-api-tool zero-trust access apps get [--account-id <ACCOUNT_ID>] --app-id <APP_ID>`
- `cloudflare-api-tool zero-trust access policies list [--account-id <ACCOUNT_ID>] --app-id <APP_ID>`
- `cloudflare-api-tool zero-trust access policies get [--account-id <ACCOUNT_ID>] --app-id <APP_ID> --policy-id <POLICY_ID>`

Tip: Zero Trust endpoints can be slow in some accounts. If a command feels "hung", retry with `--progress --timeout-profile slow`.

## Tunnels (read-only helpers)

- `cloudflare-api-tool tunnels list [--account-id <ACCOUNT_ID>] [--name "<NAME>"] [--status "<STATUS>"]`
- `cloudflare-api-tool tunnels resolve [--account-id <ACCOUNT_ID>] --name "<EXACT_NAME>"`
- `cloudflare-api-tool tunnels config get [--account-id <ACCOUNT_ID>] --tunnel-id <TUNNEL_ID>`

## Advanced: operations (all allowlisted ledgers)

This is the “full coverage” surface that can call any allowlisted endpoint **listed in the tool’s ledgers**:
- `docs/api_coverage_accounts_get.md`
- `docs/api_coverage_accounts_writes.md`
- `docs/api_coverage_workers_platform.md`
- `docs/api_coverage_workers_ai.md`
- `docs/api_coverage_vectorize.md`
- `docs/api_coverage_pages.md`
- `docs/api_coverage_images.md`
- `docs/api_coverage_ai_gateway.md`
- `docs/api_coverage_autorag.md`
- `docs/api_coverage_ai_search.md`
- `docs/api_coverage_workflows.md`
- `docs/api_coverage_zero_trust.md`
- `docs/api_coverage_dns.md`
- `docs/api_coverage_d1.md`
- `docs/api_coverage_hyperdrive.md`
- `docs/api_coverage_queues.md`
- `docs/api_coverage_r2.md`
- `docs/api_coverage_r2_catalog.md`
- `docs/api_coverage_secrets_store.md`
- `docs/api_coverage_pipelines.md`
- `docs/api_coverage_waiting_room.md`
- `docs/api_coverage_zones_get.md`
- `docs/api_coverage_zones_writes.md`

Full ledger index: `docs/api_coverage.md`.

In this monorepo, those ledgers are generated from the local Cloudflare docs snapshot under `docs/cloudflare-api-docs/`.

It refuses unknown endpoints (no guessing): only operations present in the tool’s ledgers are callable.

Search/inspect operations:
- `cloudflare-api-tool operations list [--contains "<TEXT>"] [--tag "<TAG>"] [--method GET] [--area "<AREA>"] [--limit N] [--include-sensitive] [--include-deprecated]`
- `cloudflare-api-tool operations show --area <AREA> --op <OP_KEY>`

Accounts GET (Phase 22):
- Broad Accounts read-only coverage lives in `docs/api_coverage_accounts_get.md`.
- Many of these operations are classified as sensitive output and hidden by default:
  - Discover: `cloudflare-api-tool operations list --contains /accounts/ --method GET --limit 20 --include-sensitive`
  - Apply (file-only; never printed): `cloudflare-api-tool --project-dir . --apply operations <AREA> <OP_KEY> --path-param account_id=<ACCOUNT_ID> --out ./accounts_get.json`

Accounts writes (Phase 23):
- Remaining `/accounts*` write coverage (POST/PUT/PATCH/DELETE) lives in `docs/api_coverage_accounts_writes.md` (delta ledger).
- Plan (dry-run; reads live old-state first when possible): `cloudflare-api-tool operations <AREA> <OP_KEY> --path-param account_id=<ACCOUNT_ID> [--body-json-file <FILE>]`
- Apply (file-only; never printed): `cloudflare-api-tool --project-dir . --apply --yes operations <AREA> <OP_KEY> --path-param account_id=<ACCOUNT_ID> --out ./accounts_write.json`
  - Any applied `/accounts*` write requires `--out <FILE>` (stdout never contains `result` for these operations).
  - Any applied `DELETE /accounts*` requires `--ack-irreversible` in addition to `--apply --yes`.
  - Plans and receipts include `before_state` / `before_state_path` when a matching read path exists.
  - Live apply requires explicit no-snapshot approval when the operation cannot save before-state; unsupported or failed safety-check cases still stop.
  - Receipts include best-effort read-back verification, but are redacted (no embedded response bodies).

Zones GET (Phase 24):
- Broad Zones read-only coverage lives in `docs/api_coverage_zones_get.md`.
- The Phase 24 Zones GET allowlist is classified as sensitive output and hidden by default (conservative safety model):
  - Discover (show hidden ops): `cloudflare-api-tool operations list --contains /zones/ --method GET --limit 20 --include-sensitive`
  - Apply (file-only; never printed): `cloudflare-api-tool --project-dir . --apply operations <AREA> <OP_KEY> --path-param zone_id=<ZONE_ID> --out ./zones_get.json`
- For common discovery tasks that are not hidden, prefer the dedicated `zones` commands in the “Zones” section above.

Zones writes (Phase 25):
- Remaining `/zones*` POST/PUT/PATCH/DELETE coverage lives in `docs/api_coverage_zones_writes.md`.
- Plan (dry-run; saves before-state when possible when a safe read path exists): `cloudflare-api-tool operations <AREA> <OP_KEY> --path-param zone_id=<ZONE_ID> [--body-json-file <FILE>]`
- Apply: `cloudflare-api-tool --project-dir . --apply --yes operations <AREA> <OP_KEY> ...`
  - `DELETE /zones/{zone_id}` (`zones-0-delete`) additionally requires `--ack-irreversible`.
  - Token-like results require `--ack-irreversible --out <FILE>` and are never printed.
  - Live apply requires explicit no-snapshot approval when the operation cannot save before-state; unsupported or failed safety-check cases still stop.

Call an operation (plan by default):
- For **non-sensitive read-only (GET)** operations, `operations <AREA> <OP_KEY>` executes immediately (no `--apply` needed).
- For **writes** (POST/PUT/PATCH/DELETE), `operations <AREA> <OP_KEY>` is plan-first (dry-run) by default.
- For **read-like non-GET** operations that return sensitive bodies (example: KV bulk get, Queues pull), apply requires `--apply` + `--out` and does **not** require `--yes`.

Read-only (GET) call:
- `cloudflare-api-tool operations <AREA> <OP_KEY> --path-param key=value [--query key=value ...]`

Write call (plan first, then apply):
- Plan (dry-run): `cloudflare-api-tool operations <AREA> <OP_KEY> --path-param key=value ...`
- Apply: `cloudflare-api-tool --apply --yes operations <AREA> <OP_KEY> ...`

Request body inputs (mutually exclusive):
- `--body-json-file <FILE>`
- `--body-bytes-file <FILE> [--content-type <TYPE>]`
- `--multipart-spec-file <FILE>` (JSON: `{ "fields": {...}, "files": [{ "name": "...", "path": "...", "filename": "...", "content_type": "..." }] }`)

Safety gates:
- Non-sensitive reads (GET) run with no flags.
- Writes require `--apply --yes` and saved before-state; unsupported write families require explicit no-snapshot approval for live apply.
- Broad `operations` write calls do not include a built-in tool rollback/restore path; there is no automatic undo.
- Applied `/accounts*` writes additionally require `--out <FILE>` (file-only output), and `DELETE /accounts*` additionally requires `--ack-irreversible`.
- Any file output requires `--apply` (because it writes to disk).
- Sensitive outputs (tokens/code/KV values/temporary upload JWTs/PII-like outputs) require `--apply --out <FILE>` and write the response to a local file under `--project-dir` (never printed).
- Top-level governance endpoints (for example `/user/*`, `/organizations/*`, `/memberships/*`, `/tenants/*`, `/system/*`) are treated as sensitive file-only output and are hidden from `operations list` unless you pass `--include-sensitive`.
- Vectorize v2 operations are classified as sensitive file-only output: apply requires `--apply --out <FILE>`; query/get-by-ids are read-like POSTs (no `--yes`); writes require `--yes`.
- AutoRAG operations are classified as sensitive file-only output: apply requires `--apply --out <FILE>`; `ai-search`/`search` are read-like POSTs (no `--yes`); `sync` is a state-changing PATCH (requires `--yes`).
- AI Search operations are classified as sensitive file-only output: apply requires `--apply --out <FILE>`; `search`/`chat` are read-like POSTs (no `--yes`); token create/update requires `--ack-irreversible`.
- Workers AI operations are classified as sensitive file-only output: apply requires `--apply --out <FILE>`; `operations list` hides them unless you pass `--include-sensitive`.
- Workers AI model runs (`POST /accounts/{account_id}/ai/run/...`) are treated as read-like POSTs: apply requires `--apply --out <FILE>` and does **not** require `--yes`.
- Workers AI finetunes (create/update/delete/asset upload) are state-changing: apply requires `--apply --yes --out <FILE>`.
- Pages endpoints are always sensitive file-only output: apply requires `--apply --out <FILE>`, writes require `--apply --yes --out <FILE>`, and rollback additionally requires `--ack-irreversible`.
- Images has sensitive file-only endpoints (blob/direct_upload/signing keys): `operations list` hides them unless you pass `--include-sensitive`.
- Images `direct_upload` is a read-like POST: apply requires `--apply --out <FILE>` and does **not** require `--yes`.
- AI Gateway logs/datasets/evals/provider configs are sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`. Provider config writes additionally require `--ack-irreversible`.
- Some endpoints can create/return secrets/tokens: apply requires `--ack-irreversible` and `--out <FILE>`.
- Some operations are destructive and additionally require `--ack-irreversible` even when not secret-bearing (example: `zones-0-delete`).

Vectorize notes:
- Vectorize v2 operations are classified as sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`.
- Any applied Vectorize call (including GET) requires `--apply --out <FILE>` (never printed).
- Read-like POSTs:
  - `vectorize-query-vector`
  - `vectorize-get-vectors-by-id`
  Apply requires `--apply --out <FILE>` and does **not** require `--yes` (receipts report `changed=false`).
- Write-like operations (index create/delete, insert/upsert/delete-by-ids, metadata index create/delete) require `--apply --yes --out <FILE>`.

AutoRAG notes:
- AutoRAG operations are classified as sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`.
- Any applied AutoRAG call (including GET) requires `--apply --out <FILE>` (never printed).
- Read-like POSTs:
  - `autorag-config-ai-search`
  - `autorag-config-search`
  Apply requires `--apply --out <FILE>` and does **not** require `--yes` (receipts report `changed=false`).
- `autorag-config-sync` is a state-changing PATCH (triggers a sync/job): apply requires `--apply --yes --out <FILE>`.

AI Search notes:
- AI Search operations are classified as sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`.
- Any applied AI Search call (including GET) requires `--apply --out <FILE>` (never printed).
- Read-like POSTs:
  - `ai-search-instance-search`
  - `ai-search-instance-chat-completion`
  Apply requires `--apply --out <FILE>` and does **not** require `--yes` (receipts report `changed=false`).
- Token create/update are secret-bearing write results: apply requires `--apply --yes --ack-irreversible --out <FILE>` (never printed).
- Other AI Search writes (instances create/update/delete, job create/status changes, item sync, token delete) require `--apply --yes --out <FILE>`.

Pages notes:
- Pages operations are classified as sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`.
- Any applied Pages call (including GET) requires `--apply --out <FILE>`; writes also require `--yes`.
- Rollback is gated: it also requires `--ack-irreversible`.

Pages deploy:
- `cloudflare-api-tool pages deploy --account-id <ACCOUNT_ID> --project-name <PROJECT_NAME> --source-dir <DIR> --out <FILE>`
  - Dry-run is local only: the command builds the deployment plan without calling Cloudflare.
  - Live apply requires `--apply --yes --ack-no-snapshot --out <FILE>` when no saved before-state is available for the Pages project/deployment flow.
  - Use `--branch <NAME>` to target a preview branch in the plan. Use `--production-branch <NAME>` to control the branch used if the project must be created. Use `--skip-caching` to force-upload all files in the plan. Use `--overwrite` to replace `<FILE>` if it already exists once apply support is restored.

Images notes:
- Images blob/direct_upload/signing keys operations are classified as sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`.
- Blob reads: `--apply --out <FILE>` (never printed).
- Signing key reads (list keys): `--apply --ack-irreversible --out <FILE>` (never printed).
- Direct upload URL is treated as read-like POST (no Cloudflare state change expected): apply requires `--apply --out <FILE>` and does **not** require `--yes`.
- Signing key writes (PUT/DELETE): `--apply --yes --ack-irreversible --out <FILE>` (never printed).

AI Gateway notes:
- AI Gateway logs/datasets/evals/provider configs are classified as sensitive file-only output: `operations list` hides them unless you pass `--include-sensitive`.
- Sensitive AI Gateway reads (GET) require `--apply --out <FILE>` (never printed).
- Provider config writes (POST/PUT/DELETE) require `--apply --yes --ack-irreversible --out <FILE>` (never printed).
- Endpoint reference: this tool follows the vendored OpenAPI snapshot in `docs/cloudflare-api-docs/` (the website may not show every method on every resource).

AI Gateway examples:
- Find AI Gateway operations:
  - `cloudflare-api-tool operations list --contains ai-gateway --limit 50`
  - `cloudflare-api-tool operations list --contains ai-gateway --limit 50 --include-sensitive`
- Logs (sensitive read → file):
  - `cloudflare-api-tool --apply operations ai_gateway aig-config-list-gateway-logs --path-param account_id=<ACCOUNT_ID> --path-param gateway_id=<GATEWAY_ID> --out <FILE>`
- Datasets/Evaluations (sensitive reads → file):
  - `cloudflare-api-tool --apply operations ai_gateway aig-config-list-dataset --path-param account_id=<ACCOUNT_ID> --path-param gateway_id=<GATEWAY_ID> --out <FILE>`
  - `cloudflare-api-tool --apply operations ai_gateway aig-config-list-evaluations --path-param account_id=<ACCOUNT_ID> --path-param gateway_id=<GATEWAY_ID> --out <FILE>`
- Provider configs (writes can return secrets → file):
  - `cloudflare-api-tool --apply --yes --ack-irreversible operations ai_gateway aig-config-update-providers --path-param account_id=<ACCOUNT_ID> --path-param gateway_id=<GATEWAY_ID> --path-param id=<PROVIDER_CONFIG_ID> --body-json-file <FILE> --out <FILE>`

Vectorize examples:
- Discover Vectorize operations (hidden unless include-sensitive):
  - `cloudflare-api-tool operations list --contains vectorize --limit 50`
  - `cloudflare-api-tool operations list --contains vectorize --limit 50 --include-sensitive`
- Query vectors (read-like POST; sensitive output → file; no `--yes`):
  - `cloudflare-api-tool --apply operations vectorize vectorize-query-vector --path-param account_id=<ACCOUNT_ID> --path-param index_name=<INDEX_NAME> --body-json-file <FILE> --out <FILE>`
- Get vectors by IDs (read-like POST; sensitive output → file; no `--yes`):
  - `cloudflare-api-tool --apply operations vectorize vectorize-get-vectors-by-id --path-param account_id=<ACCOUNT_ID> --path-param index_name=<INDEX_NAME> --body-json-file <FILE> --out <FILE>`
- Upsert vectors (write; sensitive output → file; requires `--yes`):
  - `cloudflare-api-tool --apply --yes operations vectorize vectorize-upsert-vector --path-param account_id=<ACCOUNT_ID> --path-param index_name=<INDEX_NAME> --body-json-file <FILE> --out <FILE>`

AutoRAG examples:
- Discover AutoRAG operations (hidden unless include-sensitive):
  - `cloudflare-api-tool operations list --contains autorag --limit 50`
  - `cloudflare-api-tool operations list --contains autorag --limit 50 --include-sensitive`
- Search (read-like POST; sensitive output → file; no `--yes`):
  - `cloudflare-api-tool --apply operations autorag autorag-config-search --path-param account_id=<ACCOUNT_ID> --path-param id=<RAG_ID> --body-json-file <FILE> --out <FILE>`
  - `cloudflare-api-tool --apply operations autorag autorag-config-ai-search --path-param account_id=<ACCOUNT_ID> --path-param id=<RAG_ID> --body-json-file <FILE> --out <FILE>`
- Sync (state-changing PATCH; sensitive output → file; requires `--yes`):
  - `cloudflare-api-tool --apply --yes operations autorag autorag-config-sync --path-param account_id=<ACCOUNT_ID> --path-param id=<RAG_ID> --out <FILE>`

AI Search examples:
- Discover AI Search operations (hidden unless include-sensitive):
  - `cloudflare-api-tool operations list --contains ai-search --limit 50`
  - `cloudflare-api-tool operations list --contains ai-search --limit 50 --include-sensitive`
- Search (read-like POST; sensitive output → file; no `--yes`):
  - `cloudflare-api-tool --apply operations ai_search ai-search-instance-search --path-param account_id=<ACCOUNT_ID> --path-param id=<INSTANCE_ID> --body-json-file <FILE> --out <FILE>`
- Chat completions (read-like POST; sensitive output → file; no `--yes`):
  - `cloudflare-api-tool --apply operations ai_search ai-search-instance-chat-completion --path-param account_id=<ACCOUNT_ID> --path-param id=<INSTANCE_ID> --body-json-file <FILE> --out <FILE>`
- Token create (secret-bearing write result; requires `--ack-irreversible`):
  - `cloudflare-api-tool --apply --yes --ack-irreversible operations ai_search ai-search-create-tokens --path-param account_id=<ACCOUNT_ID> --body-json-file <FILE> --out <FILE>`

## Jobs (batch; CSV)

Run a batch file (dry-run by default):
- `cloudflare-api-tool jobs run --file jobs.csv`
- Apply: read-only and read-like rows can run with `--apply`; write rows need saved before-state per changed resource or explicit no-snapshot approval.

Optional:
- `--include-results` includes full JSON results for non-sensitive steps in the output receipt (can be large).

CSV columns (recommended headers):
- `operation_id` (preferred when present)
- or `method` + `path` (when `operation_id` is missing)
- `path_params_json` (JSON object string)
- `query_json` (JSON object string)
- `body_json_file` / `body_bytes_file` / `multipart_spec_file` (mutually exclusive)
- `content_type` (optional)
- `out` + `overwrite` (required for sensitive steps)

Zone onboarding tip:
- Before a zone-create batch, run `cloudflare-api-tool auth zone-create-check --account-id <ACCOUNT_ID>`
- For a batch create, use `jobs run` with `operation_id=zones-post` and one row per domain.
