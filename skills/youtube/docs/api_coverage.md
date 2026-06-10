# API coverage (YouTube Data API v3)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Provide a single canonical inventory of API methods.

## Coverage definition (no fake 100%)

For this tool, “ALL capabilities” is defined as:
- Every method present in the pinned YouTube Data API v3 discovery document is callable via the CLI deterministically.

Canonical inventory source (pinned snapshot):
- `docs/official_discovery_youtube_v3_rest.json`

Derived inventory (one method per line, sorted):
- `docs/official_methods.txt`

## Current coverage status

- Method inventory: complete (pinned + test-validated against the snapshot).
- Method execution: complete via explicit per-method commands:
  - `youtube-api-tool api <resource.method>` (dry-run plan by default)
  - `youtube-api-tool --apply --yes api <resource.method>` (write attempt; currently requires explicit no-snapshot approval before provider write when no saved snapshot or provider backup is available)
  - `youtube-api-tool --apply --yes api <resource.method> --upload-file <path>` (mediaUpload write attempt; currently requires explicit no-snapshot approval before upload endpoint use)

## Method-by-method mapping (pinned discovery snapshot)

Common request-building flags for `api <resource.method>`:
- Query params:
  - `--params-json '{"key":"value"}'` (JSON object)
  - `--params-file ./params.json` (JSON file containing an object)
- JSON body:
  - `--body-json '{"key":"value"}'` (any JSON)
  - `--body-file ./body.json` (JSON file)
  - `--body-stdin` (read JSON body from stdin)
- Reads (GET):
  - Default is a deterministic dry-run plan.
  - Use `--live` to execute a GET without `--apply`.
- Writes (non-GET):
  - Default is a deterministic dry-run plan.
  - Require `--apply --yes`, then currently require explicit no-snapshot approval before provider writes when before-state/provider-backup support is not available.
  - Delete methods also require `--ack-irreversible`.
- Media upload methods:
  - Require `--apply --yes --upload-file <path>`, then currently require explicit no-snapshot approval before upload endpoint use.
  - Optional: `--upload-protocol simple|resumable` (defaults to `simple`).
- Media download methods (marked `supportsMediaDownload` in discovery; currently: `captions.download`):
  - Use `--download-to <path>` to save the response body to a file.
  - Live execution requires `--live` (GET; no `--apply` needed).

This table enumerates every `resource.method` from `docs/official_methods.txt` (derived from `docs/official_discovery_youtube_v3_rest.json`).

- `abuseReports.insert` — POST, WRITE — Plan: `youtube-api-tool api abuseReports.insert` — Apply attempt: `youtube-api-tool --apply --yes api abuseReports.insert`
- `activities.list` — GET, READ — Plan: `youtube-api-tool api activities.list` — Live read: `youtube-api-tool api activities.list --live`
- `captions.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api captions.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api captions.delete`
- `captions.download` — GET, READ, MEDIA DOWNLOAD — Plan: `youtube-api-tool api captions.download --download-to ./captions.vtt` — Live read: `youtube-api-tool api captions.download --live --download-to ./captions.vtt`
- `captions.insert` — POST, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api captions.insert` — Apply attempt: `youtube-api-tool --apply --yes api captions.insert --upload-file <path> [--upload-protocol simple|resumable]`
- `captions.list` — GET, READ — Plan: `youtube-api-tool api captions.list` — Live read: `youtube-api-tool api captions.list --live`
- `captions.update` — PUT, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api captions.update` — Apply attempt: `youtube-api-tool --apply --yes api captions.update --upload-file <path> [--upload-protocol simple|resumable]`
- `channelBanners.insert` — POST, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api channelBanners.insert` — Apply attempt: `youtube-api-tool --apply --yes api channelBanners.insert --upload-file <path> [--upload-protocol simple|resumable]`
- `channelSections.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api channelSections.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api channelSections.delete`
- `channelSections.insert` — POST, WRITE — Plan: `youtube-api-tool api channelSections.insert` — Apply attempt: `youtube-api-tool --apply --yes api channelSections.insert`
- `channelSections.list` — GET, READ — Plan: `youtube-api-tool api channelSections.list` — Live read: `youtube-api-tool api channelSections.list --live`
- `channelSections.update` — PUT, WRITE — Plan: `youtube-api-tool api channelSections.update` — Apply attempt: `youtube-api-tool --apply --yes api channelSections.update`
- `channels.list` — GET, READ — Plan: `youtube-api-tool api channels.list` — Live read: `youtube-api-tool api channels.list --live`
- `channels.update` — PUT, WRITE — Plan: `youtube-api-tool api channels.update` — Apply attempt: `youtube-api-tool --apply --yes api channels.update`
- `commentThreads.insert` — POST, WRITE — Plan: `youtube-api-tool api commentThreads.insert` — Apply attempt: `youtube-api-tool --apply --yes api commentThreads.insert`
- `commentThreads.list` — GET, READ — Plan: `youtube-api-tool api commentThreads.list` — Live read: `youtube-api-tool api commentThreads.list --live`
- `comments.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api comments.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api comments.delete`
- `comments.insert` — POST, WRITE — Plan: `youtube-api-tool api comments.insert` — Apply attempt: `youtube-api-tool --apply --yes api comments.insert`
- `comments.list` — GET, READ — Plan: `youtube-api-tool api comments.list` — Live read: `youtube-api-tool api comments.list --live`
- `comments.markAsSpam` — POST, WRITE — Plan: `youtube-api-tool api comments.markAsSpam` — Apply attempt: `youtube-api-tool --apply --yes api comments.markAsSpam`
- `comments.setModerationStatus` — POST, WRITE — Plan: `youtube-api-tool api comments.setModerationStatus` — Apply attempt: `youtube-api-tool --apply --yes api comments.setModerationStatus`
- `comments.update` — PUT, WRITE — Plan: `youtube-api-tool api comments.update` — Apply attempt: `youtube-api-tool --apply --yes api comments.update`
- `i18nLanguages.list` — GET, READ — Plan: `youtube-api-tool api i18nLanguages.list` — Live read: `youtube-api-tool api i18nLanguages.list --live`
- `i18nRegions.list` — GET, READ — Plan: `youtube-api-tool api i18nRegions.list` — Live read: `youtube-api-tool api i18nRegions.list --live`
- `liveBroadcasts.bind` — POST, WRITE — Plan: `youtube-api-tool api liveBroadcasts.bind` — Apply attempt: `youtube-api-tool --apply --yes api liveBroadcasts.bind`
- `liveBroadcasts.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api liveBroadcasts.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api liveBroadcasts.delete`
- `liveBroadcasts.insert` — POST, WRITE — Plan: `youtube-api-tool api liveBroadcasts.insert` — Apply attempt: `youtube-api-tool --apply --yes api liveBroadcasts.insert`
- `liveBroadcasts.insertCuepoint` — POST, WRITE — Plan: `youtube-api-tool api liveBroadcasts.insertCuepoint` — Apply attempt: `youtube-api-tool --apply --yes api liveBroadcasts.insertCuepoint`
- `liveBroadcasts.list` — GET, READ — Plan: `youtube-api-tool api liveBroadcasts.list` — Live read: `youtube-api-tool api liveBroadcasts.list --live`
- `liveBroadcasts.transition` — POST, WRITE — Plan: `youtube-api-tool api liveBroadcasts.transition` — Apply attempt: `youtube-api-tool --apply --yes api liveBroadcasts.transition`
- `liveBroadcasts.update` — PUT, WRITE — Plan: `youtube-api-tool api liveBroadcasts.update` — Apply attempt: `youtube-api-tool --apply --yes api liveBroadcasts.update`
- `liveChatBans.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api liveChatBans.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api liveChatBans.delete`
- `liveChatBans.insert` — POST, WRITE — Plan: `youtube-api-tool api liveChatBans.insert` — Apply attempt: `youtube-api-tool --apply --yes api liveChatBans.insert`
- `liveChatMessages.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api liveChatMessages.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api liveChatMessages.delete`
- `liveChatMessages.insert` — POST, WRITE — Plan: `youtube-api-tool api liveChatMessages.insert` — Apply attempt: `youtube-api-tool --apply --yes api liveChatMessages.insert`
- `liveChatMessages.list` — GET, READ — Plan: `youtube-api-tool api liveChatMessages.list` — Live read: `youtube-api-tool api liveChatMessages.list --live`
- `liveChatMessages.transition` — POST, WRITE — Plan: `youtube-api-tool api liveChatMessages.transition` — Apply attempt: `youtube-api-tool --apply --yes api liveChatMessages.transition`
- `liveChatModerators.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api liveChatModerators.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api liveChatModerators.delete`
- `liveChatModerators.insert` — POST, WRITE — Plan: `youtube-api-tool api liveChatModerators.insert` — Apply attempt: `youtube-api-tool --apply --yes api liveChatModerators.insert`
- `liveChatModerators.list` — GET, READ — Plan: `youtube-api-tool api liveChatModerators.list` — Live read: `youtube-api-tool api liveChatModerators.list --live`
- `liveStreams.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api liveStreams.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api liveStreams.delete`
- `liveStreams.insert` — POST, WRITE — Plan: `youtube-api-tool api liveStreams.insert` — Apply attempt: `youtube-api-tool --apply --yes api liveStreams.insert`
- `liveStreams.list` — GET, READ — Plan: `youtube-api-tool api liveStreams.list` — Live read: `youtube-api-tool api liveStreams.list --live`
- `liveStreams.update` — PUT, WRITE — Plan: `youtube-api-tool api liveStreams.update` — Apply attempt: `youtube-api-tool --apply --yes api liveStreams.update`
- `members.list` — GET, READ — Plan: `youtube-api-tool api members.list` — Live read: `youtube-api-tool api members.list --live`
- `membershipsLevels.list` — GET, READ — Plan: `youtube-api-tool api membershipsLevels.list` — Live read: `youtube-api-tool api membershipsLevels.list --live`
- `playlistImages.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api playlistImages.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api playlistImages.delete`
- `playlistImages.insert` — POST, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api playlistImages.insert` — Apply attempt: `youtube-api-tool --apply --yes api playlistImages.insert --upload-file <path> [--upload-protocol simple|resumable]`
- `playlistImages.list` — GET, READ — Plan: `youtube-api-tool api playlistImages.list` — Live read: `youtube-api-tool api playlistImages.list --live`
- `playlistImages.update` — PUT, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api playlistImages.update` — Apply attempt: `youtube-api-tool --apply --yes api playlistImages.update --upload-file <path> [--upload-protocol simple|resumable]`
- `playlistItems.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api playlistItems.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api playlistItems.delete`
- `playlistItems.insert` — POST, WRITE — Plan: `youtube-api-tool api playlistItems.insert` — Apply attempt: `youtube-api-tool --apply --yes api playlistItems.insert`
- `playlistItems.list` — GET, READ — Plan: `youtube-api-tool api playlistItems.list` — Live read: `youtube-api-tool api playlistItems.list --live`
- `playlistItems.update` — PUT, WRITE — Plan: `youtube-api-tool api playlistItems.update` — Apply attempt: `youtube-api-tool --apply --yes api playlistItems.update`
- `playlists.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api playlists.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api playlists.delete`
- `playlists.insert` — POST, WRITE — Plan: `youtube-api-tool api playlists.insert` — Apply attempt: `youtube-api-tool --apply --yes api playlists.insert`
- `playlists.list` — GET, READ — Plan: `youtube-api-tool api playlists.list` — Live read: `youtube-api-tool api playlists.list --live`
- `playlists.update` — PUT, WRITE — Plan: `youtube-api-tool api playlists.update` — Apply attempt: `youtube-api-tool --apply --yes api playlists.update`
- `search.list` — GET, READ — Plan: `youtube-api-tool api search.list` — Live read: `youtube-api-tool api search.list --live`
- `subscriptions.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api subscriptions.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api subscriptions.delete`
- `subscriptions.insert` — POST, WRITE — Plan: `youtube-api-tool api subscriptions.insert` — Apply attempt: `youtube-api-tool --apply --yes api subscriptions.insert`
- `subscriptions.list` — GET, READ — Plan: `youtube-api-tool api subscriptions.list` — Live read: `youtube-api-tool api subscriptions.list --live`
- `superChatEvents.list` — GET, READ — Plan: `youtube-api-tool api superChatEvents.list` — Live read: `youtube-api-tool api superChatEvents.list --live`
- `tests.insert` — POST, WRITE — Plan: `youtube-api-tool api tests.insert` — Apply attempt: `youtube-api-tool --apply --yes api tests.insert`
- `thirdPartyLinks.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api thirdPartyLinks.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api thirdPartyLinks.delete`
- `thirdPartyLinks.insert` — POST, WRITE — Plan: `youtube-api-tool api thirdPartyLinks.insert` — Apply attempt: `youtube-api-tool --apply --yes api thirdPartyLinks.insert`
- `thirdPartyLinks.list` — GET, READ — Plan: `youtube-api-tool api thirdPartyLinks.list` — Live read: `youtube-api-tool api thirdPartyLinks.list --live`
- `thirdPartyLinks.update` — PUT, WRITE — Plan: `youtube-api-tool api thirdPartyLinks.update` — Apply attempt: `youtube-api-tool --apply --yes api thirdPartyLinks.update`
- `thumbnails.set` — POST, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api thumbnails.set` — Apply attempt: `youtube-api-tool --apply --yes api thumbnails.set --upload-file <path> [--upload-protocol simple|resumable]`
- `videoAbuseReportReasons.list` — GET, READ — Plan: `youtube-api-tool api videoAbuseReportReasons.list` — Live read: `youtube-api-tool api videoAbuseReportReasons.list --live`
- `videoCategories.list` — GET, READ — Plan: `youtube-api-tool api videoCategories.list` — Live read: `youtube-api-tool api videoCategories.list --live`
- `videoTrainability.get` — GET, READ — Plan: `youtube-api-tool api videoTrainability.get` — Live read: `youtube-api-tool api videoTrainability.get --live`
- `videos.delete` — DELETE, WRITE, IRREVERSIBLE — Plan: `youtube-api-tool api videos.delete` — Apply attempt: `youtube-api-tool --apply --yes --ack-irreversible api videos.delete`
- `videos.getRating` — GET, READ — Plan: `youtube-api-tool api videos.getRating` — Live read: `youtube-api-tool api videos.getRating --live`
- `videos.insert` — POST, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api videos.insert` — Apply attempt: `youtube-api-tool --apply --yes api videos.insert --upload-file <path> [--upload-protocol simple|resumable]`
- `videos.list` — GET, READ — Plan: `youtube-api-tool api videos.list` — Live read: `youtube-api-tool api videos.list --live`
- `videos.rate` — POST, WRITE — Plan: `youtube-api-tool api videos.rate` — Apply attempt: `youtube-api-tool --apply --yes api videos.rate`
- `videos.reportAbuse` — POST, WRITE — Plan: `youtube-api-tool api videos.reportAbuse` — Apply attempt: `youtube-api-tool --apply --yes api videos.reportAbuse`
- `videos.update` — PUT, WRITE — Plan: `youtube-api-tool api videos.update` — Apply attempt: `youtube-api-tool --apply --yes api videos.update`
- `watermarks.set` — POST, WRITE, MEDIA UPLOAD — Plan: `youtube-api-tool api watermarks.set` — Apply attempt: `youtube-api-tool --apply --yes api watermarks.set --upload-file <path> [--upload-protocol simple|resumable]`
- `watermarks.unset` — POST, WRITE — Plan: `youtube-api-tool api watermarks.unset` — Apply attempt: `youtube-api-tool --apply --yes api watermarks.unset`
- `youtube.v3.liveChat.messages.stream` — GET, READ — Plan: `youtube-api-tool api youtube.v3.liveChat.messages.stream` — Live read: `youtube-api-tool api youtube.v3.liveChat.messages.stream --live`
- `youtube.v3.updateCommentThreads` — PUT, WRITE — Plan: `youtube-api-tool api youtube.v3.updateCommentThreads` — Apply attempt: `youtube-api-tool --apply --yes api youtube.v3.updateCommentThreads`


## How to audit coverage (local, offline)

List the pinned inventory:
- `youtube-api-tool methods list`

Filter by resource:
- `youtube-api-tool methods list --resource search`

## Last audited (UTC)

2026-03-01
