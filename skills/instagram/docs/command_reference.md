# Command reference

Use this page when you need the exact Instagram command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--config project.json`
- `--project-dir /path/to/project`
- `--output json|text`
- `--env-file .env`
- `--timeout-s 30`
- `--verbose`
- `--debug`
- `--log-file audit.jsonl`
- `--apply`
- `--yes`
- `--plan-out plan.json`
- `--plan-in plan.json`
- `--receipt-out receipt.json`
- `--ack-irreversible`
- `--run-id custom_run_id`
- `--artifacts-dir /path/to/artifacts`
- `--no-artifacts`

Runtime and audit notes:
- `--config` loads non-secret project defaults from JSON.
- `--project-dir` sets the project folder used with that config.
- `--log-file` writes a sanitized JSONL audit trail.
- `--run-id` sets the local run id for write-capable commands.
- `--artifacts-dir` overrides where local plan, refusal, and summary files are written.
- `--no-artifacts` turns off the automatic local run folder for a write command.
- Write apply attempts require explicit no-snapshot approval before Instagram HTTP or local token-file writes when no saved snapshot is available. Approved supported applies write receipts.

## Local setup

- `instagram-api-tool --output json --version`
- `instagram-api-tool onboarding [--no-write-env]`

## Auth

- `instagram-api-tool auth check`
- `instagram-api-tool auth login-url --scope instagram_business_basic,instagram_business_manage_comments [--state VALUE]`
- `instagram-api-tool auth code exchange --code YOUR_CODE`
- `instagram-api-tool auth token set --file token.json`
- `instagram-api-tool auth token status`
- `instagram-api-tool auth token exchange-long [--short-token TOKEN]`
- `instagram-api-tool auth token refresh [--long-token TOKEN]`

Auth write commands create plans. When the tool cannot save useful current token state, apply requires explicit no-snapshot approval before token exchange or local token writes.

## Users

- `instagram-api-tool users me [--fields user_id,username,account_type]`
- `instagram-api-tool users get --ig-user-id 17841400000000000 [--fields biography,followers_count,website]`

## Media

- `instagram-api-tool media list --ig-user-id 17841400000000000 [--fields id,caption,media_type,permalink] [--limit 25] [--before CURSOR] [--after CURSOR]`
- `instagram-api-tool media container get --container-id 17890000000000000 [--fields id,status_code,status]`
- `instagram-api-tool media publish-limit --ig-user-id 17841400000000000 [--fields quota_usage,config]`
- `instagram-api-tool media get --media-id 17900000000000000 [--fields id,caption,comments_count,media_type]`
- `instagram-api-tool media children --media-id 17900000000000000 [--fields id,media_type,permalink]`
- `instagram-api-tool media create-container --ig-user-id 17841400000000000 --image-url https://example.invalid/image.jpg [--caption TEXT] [--media-type IMAGE]`
- `instagram-api-tool media create-container --ig-user-id 17841400000000000 --video-url https://example.invalid/video.mp4 [--caption TEXT] [--media-type REELS]`
- `instagram-api-tool media create-container --ig-user-id 17841400000000000 --children CHILD_ID_1,CHILD_ID_2 [--caption TEXT] [--media-type CAROUSEL]`
- `instagram-api-tool media publish --ig-user-id 17841400000000000 --creation-id 17890000000000000`
- `instagram-api-tool media comments set --media-id 17900000000000000 --enabled true|false`

## Comments

- `instagram-api-tool comments list --media-id 17900000000000000 [--fields id,text,username,timestamp]`
- `instagram-api-tool comments create --media-id 17900000000000000 --message "Thanks for the comment"`
- `instagram-api-tool comments get --comment-id 18000000000000000 [--fields id,text,hidden,username]`
- `instagram-api-tool comments hide --comment-id 18000000000000000 --hidden true|false`
- `instagram-api-tool comments delete --comment-id 18000000000000000`
- `instagram-api-tool comments replies list --comment-id 18000000000000000`
- `instagram-api-tool comments replies create --comment-id 18000000000000000 --message "Reply text"`

## Mentions

- `instagram-api-tool mentions media --ig-user-id 17841400000000000 --media-id 17900000000000000`
- `instagram-api-tool mentions comment --ig-user-id 17841400000000000 --comment-id 18000000000000000`
- `instagram-api-tool mentions reply-media --ig-user-id 17841400000000000 --media-id 17900000000000000 --message "Reply text"`
- `instagram-api-tool mentions reply-comment --ig-user-id 17841400000000000 --media-id 17900000000000000 --comment-id 18000000000000000 --message "Reply text"`

## Insights

- `instagram-api-tool insights account get --ig-user-id 17841400000000000 --metric impressions,reach [--period day] [--breakdown follow_type]`
- `instagram-api-tool insights media get --media-id 17900000000000000 --metric impressions,reach,saved [--period lifetime] [--breakdown action_type]`

## Messages

- `instagram-api-tool messages send --ig-user-id 17841400000000000 --recipient-id 123456789 --message "Hello"`
- `instagram-api-tool messages private-reply --ig-user-id 17841400000000000 --recipient-id 123456789 --message "Thanks for reaching out"`

## Tags, stories, and live media

- `instagram-api-tool tags list --ig-user-id 17841400000000000 [--fields id,caption,media_type]`
- `instagram-api-tool stories list --ig-user-id 17841400000000000 [--fields id,media_type,permalink]`
- `instagram-api-tool live-media list --ig-user-id 17841400000000000 [--fields id,status,title]`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.
Refusals caused by missing approval or failed safety checks save plans and summaries. Approved supported applies save receipts.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `instagram-api-tool runs list [--limit 20]`
- `instagram-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`
