# Command reference

Use this page when you need the exact Threads command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding and runs

- `threads-api-tool onboarding [--no-write-env]`
- `threads-api-tool runs list [--limit <n>]`
- `threads-api-tool runs show --run-id <run_id>`

## Auth

- `threads-api-tool auth check`
- `threads-api-tool auth authorize-url [--scope <scopes>] [--state <value>]`
- `threads-api-tool auth code exchange --code <auth_code>`
- `threads-api-tool auth token status`
- `threads-api-tool auth token exchange-long [--short-token <token>]`
- `threads-api-tool auth token refresh [--long-token <token>]`
- `threads-api-tool auth app-token generate`
- `threads-api-tool auth debug-token [--input-token <token>]`

Auth write safety:
- `auth code exchange`, `auth token exchange-long`, and `auth token refresh` are dry-run by default.
- Add `--apply` only to collect the current safety refusal. The tool requires explicit no-snapshot approval before Threads token HTTP calls or `.state/token.json` writes.

## Profiles

- `threads-api-tool profiles me [--fields <fields>]`
- `threads-api-tool profiles get --threads-user-id <id> [--fields <fields>]`
- `threads-api-tool profiles lookup --username <handle> [--fields <fields>]`

## Posts

- `threads-api-tool posts list-owned [--threads-user-id <id>] [--fields <fields>] [--limit <n>] [--before <cursor>] [--after <cursor>] [--since <cursor>] [--until <cursor>] [--reverse]`
- `threads-api-tool posts list-public --username <handle> [--fields <fields>] [--limit <n>] [--before <cursor>] [--after <cursor>] [--since <cursor>] [--until <cursor>] [--reverse]`
- `threads-api-tool posts get --threads-media-id <id> [--fields <fields>]`
- `threads-api-tool posts limits [--threads-user-id <id>]`
- `threads-api-tool posts status --threads-container-id <id> [--fields <fields>]`
- `threads-api-tool posts create-text --threads-user-id <id> --text <text> [write flags]`
- `threads-api-tool posts create-image --threads-user-id <id> --image-url <url> [write flags]`
- `threads-api-tool posts create-video --threads-user-id <id> --video-url <url> [write flags]`
- `threads-api-tool posts create-carousel-item --threads-user-id <id> (--image-url <url> | --video-url <url>) [write flags]`
- `threads-api-tool posts create-carousel --threads-user-id <id> --children <id1,id2,...> [write flags]`
- `threads-api-tool posts publish --threads-user-id <id> --threads-container-id <id>`
- `threads-api-tool posts repost --threads-media-id <id>`
- `threads-api-tool posts delete --threads-media-id <id>`

Write flags:
- Shared: `--topic-tag`, `--reply-to-id`, `--reply-control`, `--enable-reply-approvals`, `--quote-post-id`, `--location-id`
- Text-only attachments: `--link-attachment`, `--gif-id`, `--gif-provider`, `--poll-option`, `--poll-options`
- Spoilers: `--spoiler-media`, `--text-spoiler-range <offset:length>` (repeatable)
- Carousel helpers: `--children`, `--is-carousel-item`

Write safety:
- All write commands are dry-run by default.
- Add `--apply` only to collect the current safety refusal. The tool requires explicit no-snapshot approval before Threads provider writes or receipt output.
- Add `--yes --ack-irreversible` for `posts delete` before the refusal point.

## Replies

- `threads-api-tool replies list --threads-media-id <id> [--fields <fields>] [--limit <n>] [--before <cursor>] [--after <cursor>] [--since <cursor>] [--until <cursor>] [--reverse]`
- `threads-api-tool replies conversation --threads-media-id <id> [--fields <fields>] [--limit <n>]`
- `threads-api-tool replies hide --threads-reply-id <id> --hide true|false`
- `threads-api-tool replies pending list --threads-media-id <id> [--fields <fields>] [--limit <n>] [--before <cursor>] [--after <cursor>]`
- `threads-api-tool replies pending decide --threads-reply-id <id> --approve true|false`

## Mentions

- `threads-api-tool mentions list [--threads-user-id <id>] [--fields <fields>] [--limit <n>] [--before <cursor>] [--after <cursor>]`

## Insights

- `threads-api-tool insights media --threads-media-id <id> [--fields <fields>] [--since <time>] [--until <time>] [--period <period>] [--metric <list>]`
- `threads-api-tool insights user [--threads-user-id <id>] [--fields <fields>] [--since <time>] [--until <time>] [--period <period>] [--metric <list>]`

## Search

- `threads-api-tool search keyword --q <term> [--fields <fields>] [--limit <n>] [--search-type <value>] [--search-mode <value>] [--media-type <value>]`
- `threads-api-tool search topic-tag --topic-tag <tag> [--fields <fields>] [--limit <n>] [--search-type <value>] [--search-mode <value>] [--media-type <value>]`
- `threads-api-tool search recent-keywords`

## Locations

- `threads-api-tool locations search-query --q <query> [--fields <fields>]`
- `threads-api-tool locations search-coordinates --latitude <lat> --longitude <lon> [--fields <fields>]`
- `threads-api-tool locations get --location-id <id> [--fields <fields>]`

## oEmbed

- `threads-api-tool oembed get --url <threads_url> [--fields <fields>] [--maxwidth <n>]`
