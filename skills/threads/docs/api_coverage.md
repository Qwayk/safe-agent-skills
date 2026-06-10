# API coverage

Purpose:
- Make endpoint coverage explicit.
- Keep the shipped CLI tied to the current official Threads documentation.

## Summary

- Provider: Threads Graph API
- Graph host: `https://graph.threads.net`
- Version: explicit via `THREADS_API_VERSION`, default `v1.0`
- Last audited (UTC): 2026-05-26

## Ledger

| Endpoint | Capability | Commands | Status | Notes |
|---|---|---|---|---|
| `POST /oauth/access_token` | Authorization-code exchange | `auth code exchange` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available or token-file writes. |
| `GET /oauth/access_token` | App access token | `auth app-token generate` | live-unverified | Used directly and by `oembed get`. |
| `GET /access_token` | Short-lived to long-lived token exchange | `auth token exchange-long` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available or token-file writes. |
| `GET /refresh_access_token` | Long-lived token refresh | `auth token refresh` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available or token-file writes. |
| `GET /debug_token` | Token inspection | `auth debug-token` | live-unverified | Provider response is passed through with redaction. |
| `GET /me` | Current user profile | `auth check`, `profiles me` | live-unverified | `auth check` is the onboarding smoke test. |
| `GET /me?fields=recently_searched_keywords` | Recent search history | `search recent-keywords` | live-unverified | Implemented as a field-specific `GET /me` read. |
| `GET /{threads-user-id}` | Profile by user ID | `profiles get` | live-unverified | Reads documented profile fields. |
| `GET /profile_lookup` | Public profile discovery | `profiles lookup` | live-unverified | Permission-gated by `threads_profile_discovery`. |
| `GET /{threads-user-id}/threads` | Owned posts list | `posts list-owned` | live-unverified | Supports fields and pagination args. |
| `GET /profile_posts` | Public posts list | `posts list-public` | live-unverified | Uses documented `username` query parameter. |
| `GET /{threads-media-id}` | Media retrieval and container status | `posts get`, `posts status` | live-unverified | Also covers quote, repost, poll, GIF, spoiler, and location retrieval fields. |
| `GET /{threads-user-id}/threads_publishing_limit` | Publishing limits | `posts limits` | live-unverified | Read-only rate-limit metadata. |
| `POST /{threads-user-id}/threads` | Create Threads media container | `posts create-text`, `posts create-image`, `posts create-video`, `posts create-carousel-item`, `posts create-carousel` | blocked-before-write | Local tests cover official request-shape mapping; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available. |
| `POST /{threads-user-id}/threads_publish` | Publish media container | `posts publish` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available. |
| `POST /{threads-media-id}/repost` | Repost a post | `posts repost` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available. |
| `DELETE /{threads-media-id}` | Delete a post | `posts delete` | blocked-before-write | Requires `--apply --yes --ack-irreversible`, then requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available. |
| `GET /{threads-media-id}/replies` | Replies list | `replies list` | live-unverified | Supports documented paging fields. |
| `GET /{threads-media-id}/conversation` | Reply conversation view | `replies conversation` | live-unverified | Read-only conversation thread retrieval. |
| `POST /{threads-reply-id}/manage_reply` | Hide or unhide a reply | `replies hide` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available. |
| `GET /{threads-media-id}/pending_replies` | Pending replies list | `replies pending list` | live-unverified | Requires reply approvals on the post. |
| `POST /{threads-reply-id}/manage_pending_reply` | Approve or ignore a pending reply | `replies pending decide` | blocked-before-write | Dry-run plan only; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available. |
| `GET /{threads-user-id}/mentions` | Mentions list | `mentions list` | live-unverified | Permission-gated by `threads_manage_mentions`. |
| `GET /{threads-media-id}/insights` | Media insights | `insights media` | live-unverified | Permission-gated by `threads_manage_insights`. |
| `GET /{threads-user-id}/threads_insights` | User insights | `insights user` | live-unverified | Permission-gated by `threads_manage_insights`. |
| `GET /keyword_search` | Keyword and topic-tag search | `search keyword`, `search topic-tag` | live-unverified | Permission-gated by `threads_keyword_search`. |
| `GET /location_search` | Location search | `locations search-query`, `locations search-coordinates` | live-unverified | Permission-gated by `threads_location_tagging`. Before provider approval, search results are limited by Meta to the query `Menlo Park`. |
| `GET /{location-id}` | Location lookup by ID | `locations get` | live-unverified | Official Threads locations reference endpoint. |
| `GET /oembed` | oEmbed lookup | `oembed get` | live-unverified | Uses an app access token from the official client-credentials flow. |
| `Web Intents` | Share links and browser intents | docs only | non-API/dash-gated | Documented by Threads but intentionally not exposed as CLI commands. |
| `Webhook dashboard setup` | App webhook onboarding | docs only | non-API/dash-gated | Dashboard-only setup, not a Graph API CLI command. |
| `Webhook topic mapping` | Webhook topic subscription | docs only | non-API/dash-gated | Dashboard-only setup, not a Graph API CLI command. |

## Deliberate exclusions

- `posts list-ghost` is not shipped because the current public Threads docs audited for this tool do not expose a documented ghost-post endpoint.
- `replies list-user` is not shipped because the current public Threads docs audited for this tool do not expose a documented user-replies endpoint.

## Status policy

- `live-unverified`: implemented, request shape locally tested where possible, but not exercised here against live Threads accounts.
- `blocked-before-write`: write plan shape is implemented, but current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available or local token/write output when no saved snapshot is available.
- `non-API/dash-gated`: documented Threads surface that is not a Graph API endpoint command.
