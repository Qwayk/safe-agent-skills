# Command reference

Use this page when you need the exact Plausible command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags (all commands)

- `--version`: print the tool version and exit (machine-readable in `--output json`)
- `--env-file` (default: `.env`): load Plausible config from this file
- `--config`: optional non-secret project config JSON (paths/defaults)
- `--project-dir`: optional project root dir for outputs
- `--output` (`json` or `text`, default: `json`): stdout format (automation should use `json`)
- `--verbose`: prints HTTP start/end lines to stderr (never prints auth headers)
- `--log-file`: optional JSONL audit log (secrets redacted)
- `--timeout-s`: override `PLAUSIBLE_TIMEOUT_S`
- `--debug`: show stack traces on errors
- `--apply`: enable writes (otherwise write commands are dry-run)
- `--yes`: extra confirmation for writes that mutate data
- `--plan-out PATH`: write the computed plan JSON to a file (v2, no secrets)
- `--receipt-out PATH`: write the post-apply receipt JSON to a file (v2, no secrets)
- `--ack-irreversible`: extra acknowledgement for irreversible actions (v2)

## Write recovery contract

Write plans include `plan.recovery`.
Apply receipts include `receipt.recovery`.

This tool currently uses:

- `irreversible_and_clearly_labeled`
- `rollback_by_inverse_action`

Current map:

- `event send` -> `irreversible_and_clearly_labeled`
- `site create`, `site update`, `site delete`, `site goals delete`, and `site shared-links ensure` -> `irreversible_and_clearly_labeled`
- `site goals ensure`, `site custom-props ensure`, `site custom-props delete`, and `site guests ensure` -> `rollback_by_inverse_action`
- `site guests delete` -> `rollback_by_inverse_action` when the existing guest role is known, otherwise `irreversible_and_clearly_labeled`

Special note:
- `site guests delete` can only be fully reversible when the command can read the current guest role; if that role is unavailable, it remains irreversible.

Before-state capture:
- The write commands below add `before_state` to `plan`/`receipt`, and save `before_state_path` under `--env-file` directory:
  - `site create`, `site update`, `site delete`
  - `site goals ensure`, `site goals delete`
  - `site custom-props ensure`, `site custom-props delete`
  - `site guests ensure`
  - `site guests delete` (only when role is present in prior guest state)
- This CLI cannot add before-state for:
  - `event send` (no API read for exact event state)
  - `site shared-links ensure` (no read/list endpoint to fetch prior link state)

## Auth

<!-- Note: examples use module execution; you can also use the installed script `plausible-api-tool` -->

- `python3 -m plausible_api_tool auth check`

## Stats (read-only)

- Raw query (any Stats API v2 option):
  - `python3 -m plausible_api_tool stats query --file query.json`
  - `python3 -m plausible_api_tool stats query --query '{"metrics":["visitors"],"date_range":"7d"}'`
  - `cat query.json | python3 -m plausible_api_tool stats query --stdin`
- Validate query JSON:
  - `python3 -m plausible_api_tool stats validate --file query.json`
- Pages:
  - `python3 -m plausible_api_tool stats pages top --metric pageviews --days 30 --limit 50`
- Sources/referrers:
  - `python3 -m plausible_api_tool stats sources --dimension visit:channel --days 30 --limit 50`
  - `python3 -m plausible_api_tool stats referrers --days 30 --limit 50`
- Entry/exit pages:
  - `python3 -m plausible_api_tool stats entry-exit --type both --days 30 --limit 50`
- Devices:
  - `python3 -m plausible_api_tool stats devices --dimension visit:device --days 30 --limit 50`
- Goals (existing helpers):
  - `python3 -m plausible_api_tool stats goals list --date-range 30d --limit 50`
  - `python3 -m plausible_api_tool stats goals timeseries --goal "member_gate_cta_click" --date-range 30d`
  - `python3 -m plausible_api_tool stats goals breakdown --goal "members_modal_shown_manual" --prop placement --date-range 30d`
- Goals (power tools):
  - `python3 -m plausible_api_tool stats goal breakdown --goal "members_modal_shown_manual" --prop placement --days 30 --limit 50 --offset 0`
  - `python3 -m plausible_api_tool stats goal pages --goal "member_gate_cta_click" --days 30 --limit 50`
- Membership funnel:
  - `python3 -m plausible_api_tool stats funnel members --days 30`
- Compare:
  - `python3 -m plausible_api_tool stats compare --file query.json --range 7d --compare previous`

### Pagination note

Stats API v2 uses the `pagination` object (`{"limit": 100, "offset": 0}`), not a top-level `limit`.
This tool handles that for the built-in `goals` commands.

## Events (write; disabled by default)

- Dry-run (safe no-op): `python3 -m plausible_api_tool event send --name test_event --url https://example.com/`
- Live apply for this command family requires explicit no-snapshot approval when before-state persistence is not available.
- Optional fields:
  - `--referrer https://example.com/from`
  - `--revenue-currency USD --revenue-amount 9.99`

### Event send safety

`event send` refuses when:
- Any prop key/value looks like PII (example: `email`, `token`, values that look like email addresses)
- `--referrer` looks like PII or contains sensitive keywords
- `--domain` differs from `PLAUSIBLE_SITE_ID` unless you pass `--allow-non-default-domain`
- URL host does not match the event domain unless you pass `--allow-url-host-mismatch`
- Only one of `--revenue-currency` / `--revenue-amount` is provided (both are required together)

### Event send verification (best effort)

If you use a unique URL path (recommended), verification is available after a successful apply.
Apply is currently blocked for event send, so this verification path is not runnable yet.

- `Live apply requires explicit no-snapshot approval for this command family when no saved snapshot is available.`

## Sites (safe reads + gated writes)

This uses the official Sites API v1 (`/api/v1/sites` and subpaths).

Read-only:
- List sites: `python3 -m plausible_api_tool site list`
- Get a site: `python3 -m plausible_api_tool site get --site-id example.com`
- List teams: `python3 -m plausible_api_tool site teams list`
- List goals: `python3 -m plausible_api_tool site goals list --site-id example.com`
- List custom properties: `python3 -m plausible_api_tool site custom-props list --site-id example.com`
- List guests: `python3 -m plausible_api_tool site guests list --site-id example.com`

Writes (dry-run by default; requires `--apply --yes`):
- Create a site (dry-run plan): `python3 -m plausible_api_tool site create --domain test-domain.com`
- Create a site (apply): `python3 -m plausible_api_tool --apply --yes site create --domain test-domain.com --timezone Etc/UTC`
- Update a site (apply): `python3 -m plausible_api_tool --apply --yes site update --site-id test-domain.com --domain new-test-domain.com`
- Delete a site (destructive; apply): `python3 -m plausible_api_tool --apply --yes --ack-irreversible site delete --site-id test-domain.com`

Other Sites API writes:
- Ensure a shared link (dry-run plan only): `python3 -m plausible_api_tool site shared-links ensure --site-id example.com --name Wordpress`
  - recovery: `irreversible_and_clearly_labeled`
- Ensure a goal (event): `python3 -m plausible_api_tool --apply --yes site goals ensure --site-id example.com --goal-type event --event-name Signup`
  - recovery: `rollback_by_inverse_action` via `site goals delete`
- Ensure a goal (page): `python3 -m plausible_api_tool --apply --yes site goals ensure --site-id example.com --goal-type page --page-path /register`
  - recovery: `rollback_by_inverse_action` via `site goals delete`
- Delete a goal (destructive): `python3 -m plausible_api_tool --apply --yes --ack-irreversible site goals delete --site-id example.com --goal-id 123`
  - recovery: `irreversible_and_clearly_labeled`
- Ensure a custom property: `python3 -m plausible_api_tool --apply --yes site custom-props ensure --site-id example.com --property title`
  - recovery: `rollback_by_inverse_action` via `site custom-props delete`
- Delete a custom property (destructive): `python3 -m plausible_api_tool --apply --yes --ack-irreversible site custom-props delete --site-id example.com --property title`
  - recovery: `rollback_by_inverse_action` via `site custom-props ensure`
- Ensure a guest: `python3 -m plausible_api_tool --apply --yes site guests ensure --site-id example.com --email user@example.com --role viewer`
  - recovery: `rollback_by_inverse_action` via `site guests delete`
- Delete a guest membership/invite (destructive): `python3 -m plausible_api_tool --apply --yes --ack-irreversible site guests delete --site-id example.com --email user@example.com`
  - recovery: `rollback_by_inverse_action` when the removed guest role is known, else `irreversible_and_clearly_labeled`

## Reports (read-only)

- Weekly snapshot:
  - `python3 -m plausible_api_tool report weekly --days 7 --limit 50`
  - `python3 -m plausible_api_tool report weekly --days 7 --limit 50 --out-dir <PROJECT_DIR>/plausible-analytics/reports`
  - Or set a default export dir via `--config` using `reports_out_dir`
- Membership snapshot:
  - `python3 -m plausible_api_tool report membership --days 30 --limit 50`
