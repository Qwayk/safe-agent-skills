# API coverage

Last audited (UTC): 2026-06-04

Provider: Meta Instagram Platform
Product choice: Instagram API with Instagram Login
Primary API base URL: `https://graph.instagram.com`
Auth method: OAuth authorization code, then short-lived to long-lived Instagram User access token
Default API version: `v25.0`

This file is the source of truth for what this tool will ship for the Instagram Login product choice.

## Shipped Instagram Login surface

| Endpoint / operation | Capability | Planned CLI command(s) | Safety model | Notes |
|---|---|---|---|---|
| `GET /me` | Resolve the app user's Instagram professional account from the current token | `auth check`, `users me` | Read-only | Special endpoint on `graph.instagram.com` |
| `GET /{ig_user_id}` | Get IG User fields | `users get --ig-user-id ...` | Read-only | Supports explicit `--fields` |
| `GET /{ig_user_id}/media` | List owned media | `media list --ig-user-id ...` | Read-only | Read family |
| `POST /{ig_user_id}/media` | Create a publishing container | `media create-container ...` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Single image, video, reel, story, carousel container creation |
| `POST /{ig_user_id}/media_publish` | Publish an IG container | `media publish --ig-user-id ... --creation-id ...` | Plan first; `--apply --yes` plus explicit no-snapshot approval when no useful before-state can be saved | User-facing remote publish |
| `GET /{ig_container_id}` | Read container status | `media container get --container-id ...` | Read-only | Used for publish readiness and troubleshooting |
| `GET /{ig_user_id}/content_publishing_limit` | Read current publish quota usage | `media publish-limit --ig-user-id ...` | Read-only | IG Login content-publish quota view |
| `GET /{ig_media_id}` | Get IG Media fields | `media get --media-id ...` | Read-only | Supports explicit `--fields` |
| `GET /{ig_media_id}/children` | List carousel children | `media children --media-id ...` | Read-only | Albums only |
| `POST /{ig_media_id}` with `comment_enabled` | Enable or disable comments on media | `media comments set --media-id ... --enabled true|false` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Live video not supported |
| `GET /{ig_media_id}/comments` | List top-level comments on media | `comments list --media-id ...` | Read-only | Replies can be expanded or fetched separately |
| `POST /{ig_media_id}/comments` | Add a comment on owned media | `comments create --media-id ... --message ...` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Live video not supported |
| `GET /{ig_comment_id}` | Get one comment | `comments get --comment-id ...` | Read-only | Supports explicit `--fields` |
| `GET /{ig_comment_id}/replies` | List replies on a comment | `comments replies list --comment-id ...` | Read-only | Read family |
| `POST /{ig_comment_id}/replies` | Reply to a comment | `comments replies create --comment-id ... --message ...` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Private reply is a separate flow |
| `POST /{ig_comment_id}` with `hide` | Hide or unhide a comment | `comments hide --comment-id ... --hidden true|false` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Media-owner token required |
| `DELETE /{ig_comment_id}` | Delete a comment | `comments delete --comment-id ...` | Plan first; `--apply --yes --ack-irreversible` plus explicit no-snapshot approval when no useful before-state can be saved | Destructive |
| `GET /{ig_user_id}?fields=mentioned_media.media_id(...)` | Read media where the app user was mentioned in a caption | `mentions media get --ig-user-id ... --media-id ...` | Read-only | Webhook-driven lookup |
| `GET /{ig_user_id}?fields=mentioned_comment.comment_id(...)` | Read comment where the app user was mentioned | `mentions comment get --ig-user-id ... --comment-id ...` | Read-only | Webhook-driven lookup |
| `POST /{ig_user_id}/mentions` with `media_id,message` | Reply to a media caption mention | `mentions reply-media --ig-user-id ... --media-id ... --message ...` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Stories not supported |
| `POST /{ig_user_id}/mentions` with `media_id,comment_id,message` | Reply to a comment mention | `mentions reply-comment --ig-user-id ... --media-id ... --comment-id ... --message ...` | Plan first; approved apply requires explicit no-snapshot approval when no useful before-state can be saved | Stories not supported |
| `GET /{ig_user_id}/tags` | List media where the app user was tagged | `tags list --ig-user-id ...` | Read-only | Private media not returned |
| `GET /{ig_user_id}/stories` | List current stories | `stories list --ig-user-id ...` | Read-only | Stories only live for 24 hours |
| `GET /{ig_user_id}/live_media` | List live media still being broadcast | `live-media list --ig-user-id ...` | Read-only | Time-based pagination supported |
| `GET /{ig_user_id}/insights` | Get account insights | `insights account get --ig-user-id ...` | Read-only | Uses explicit metric and breakdown args |
| `GET /{ig_media_id}/insights` | Get media insights | `insights media get --media-id ...` | Read-only | Story insights webhooks not supported for IG Login |
| `POST /{ig_user_id}/messages` or `POST /me/messages` | Send a message or private reply | `messages send --ig-user-id ...`, `messages private-reply ...` | Plan first; `--apply --yes` plus explicit no-snapshot approval when no useful before-state can be saved | 24-hour rules apply; private reply has its own time limits |
| `POST /oauth/access_token` | Exchange auth code for short-lived token | `auth code exchange --code ...` | Plan only; apply requires explicit no-snapshot approval before auth HTTP or local token write | Uses `api.instagram.com` |
| `GET /access_token` | Exchange short-lived token for long-lived token | `auth token exchange-long` | Plan only; apply requires explicit no-snapshot approval before auth HTTP or local token write | Uses `graph.instagram.com` |
| `GET /refresh_access_token` | Refresh a long-lived token | `auth token refresh` | Plan only; apply requires explicit no-snapshot approval before auth HTTP or local token write | Uses `graph.instagram.com` |
| `GET /{ig_user_id}/connected_threads_user` | Read connected Threads account ID | `excluded` | Excluded by product choice | Requires Facebook User access token |
| `GET/POST /{ig_user_id}/instagram_backed_threads_user` | Read or create Instagram-backed Threads account | `excluded` | Excluded by product choice | Requires Facebook User access token |

## Excluded by product choice

These are official Meta Instagram/related capabilities, but they are not part of this tool because the user fixed the product choice to Instagram Login:

| Capability | Official docs status | Reason excluded |
|---|---|---|
| Business Discovery | Official Meta feature | Available only for Instagram API with Facebook Login |
| Hashtag Search (`ig_hashtag_search`, `IG Hashtag`, `recently_searched_hashtags`) | Official Meta feature | Available only for Facebook Login / Instagram Public Content Access flow |
| Page lookup to connected IG User | Official Meta feature | Facebook Page node; Facebook Login only |
| Product tags on media | Official Meta feature | Available only for Instagram API with Facebook Login |
| Media delete | Official Meta feature | IG media delete doc says Facebook Login only |
| Collaborative media read / search | Official Meta feature | Official docs mark it Facebook-Login-only |
| Threads account edges | Official Meta feature | Official docs require Facebook User access token |

## Official-reference gaps to watch

- `agencies`
- `authorized_adaccounts`
- `upcoming_events`
- `collaboration_invites`

These edges are listed in the official `IG User` edge table, but the public static reference pages were not retrievable during the 2026-05-22 audit. Do not claim them as shipped until Meta exposes usable reference details for request syntax, permissions, and response shape.
