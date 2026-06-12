# References (sources)

Use this page when you want to see the official YouTube and Google sources behind this tool.

Prefer official provider docs; use other sources only when needed and note why.

Source rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Google (YouTube Data API v3)
- API docs home: https://developers.google.com/youtube/v3/docs
- Reference: https://developers.google.com/youtube/v3/docs/reference
- Discovery doc (canonical method inventory): https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest
- Auth guide: https://developers.google.com/youtube/v3/guides/authentication
- Quota/usage limits: https://developers.google.com/youtube/v3/getting-started#quota
- Uploads guide: https://developers.google.com/youtube/v3/guides/implementation/uploading_a_video
- Method docs (used by `channels` commands):
  - `channels.list`: https://developers.google.com/youtube/v3/docs/channels/list
    - Note: `forHandle` accepts either `HandleName` or `@HandleName` (official docs).
  - `playlistItems.list`: https://developers.google.com/youtube/v3/docs/playlistItems/list
  - `videos.list`: https://developers.google.com/youtube/v3/docs/videos/list
  - `search.list`: https://developers.google.com/youtube/v3/docs/search/list
- Last verified (UTC): 2026-03-01

## Other sources (only if needed)
None.
