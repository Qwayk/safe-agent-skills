# API coverage (Reddit Data API)

Purpose:
- Make official Reddit REST coverage measurable.
- Keep `api <operation>` commands tied to a pinned official docs snapshot.

## Summary

- Provider: Reddit Data API (`/dev/api`)
- Base URL (default): `https://oauth.reddit.com`
- Auth: OAuth 2.0 bearer token for a registered Reddit app
- Pinned docs snapshot: `docs/official_api_docs_2026-05-22.html`
- Total operations in snapshot: **234**
- Last audited (UTC): 2026-05-22

## Inventory mapping

Definition of coverage for this tool:
- Every row below must be available as an explicit CLI subcommand under `qwayk-reddit-safe-agent-cli api <operation_command>`.
- No raw request bridge counts toward coverage.

| operation_command | METHOD | PATH | section | oauth_scope | primary_cli |
|---|---:|---|---|---|---|
| `get-api-v1-me` | `GET` | `/api/v1/me` | `account` | `identity` | `qwayk-reddit-safe-agent-cli api get-api-v1-me` |
| `get-api-v1-me-karma` | `GET` | `/api/v1/me/karma` | `account` | `mysubreddits` | `qwayk-reddit-safe-agent-cli api get-api-v1-me-karma` |
| `get-api-v1-me-prefs` | `GET` | `/api/v1/me/prefs` | `account` | `identity` | `qwayk-reddit-safe-agent-cli api get-api-v1-me-prefs` |
| `patch-api-v1-me-prefs` | `PATCH` | `/api/v1/me/prefs` | `account` | `account` | `qwayk-reddit-safe-agent-cli api patch-api-v1-me-prefs` |
| `get-api-v1-me-trophies` | `GET` | `/api/v1/me/trophies` | `account` | `identity` | `qwayk-reddit-safe-agent-cli api get-api-v1-me-trophies` |
| `get-prefs-friends` | `GET` | `/prefs/friends` | `account` | `read` | `qwayk-reddit-safe-agent-cli api get-prefs-friends` |
| `get-prefs-blocked` | `GET` | `/prefs/blocked` | `account` | `read` | `qwayk-reddit-safe-agent-cli api get-prefs-blocked` |
| `get-prefs-messaging` | `GET` | `/prefs/messaging` | `account` | `read` | `qwayk-reddit-safe-agent-cli api get-prefs-messaging` |
| `get-prefs-trusted` | `GET` | `/prefs/trusted` | `account` | `read` | `qwayk-reddit-safe-agent-cli api get-prefs-trusted` |
| `get-api-v1-me-friends` | `GET` | `/api/v1/me/friends` | `account` | `read` | `qwayk-reddit-safe-agent-cli api get-api-v1-me-friends` |
| `get-api-v1-me-blocked` | `GET` | `/api/v1/me/blocked` | `account` | `read` | `qwayk-reddit-safe-agent-cli api get-api-v1-me-blocked` |
| `get-api-announcements-v1-unread` | `GET` | `/api/announcements/v1/unread` | `announcements` | `announcements` | `qwayk-reddit-safe-agent-cli api get-api-announcements-v1-unread` |
| `post-api-announcements-v1-hide` | `POST` | `/api/announcements/v1/hide` | `announcements` | `announcements` | `qwayk-reddit-safe-agent-cli api post-api-announcements-v1-hide` |
| `post-api-announcements-v1-read` | `POST` | `/api/announcements/v1/read` | `announcements` | `announcements` | `qwayk-reddit-safe-agent-cli api post-api-announcements-v1-read` |
| `post-api-announcements-v1-read-all` | `POST` | `/api/announcements/v1/read_all` | `announcements` | `announcements` | `qwayk-reddit-safe-agent-cli api post-api-announcements-v1-read-all` |
| `get-api-needs-captcha` | `GET` | `/api/needs_captcha` | `captcha` | `any` | `qwayk-reddit-safe-agent-cli api get-api-needs-captcha` |
| `post-api-v1-subreddit-emoji-json` | `POST` | `/api/v1/{subreddit}/emoji.json` | `emoji` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api post-api-v1-subreddit-emoji-json` |
| `delete-api-v1-subreddit-emoji-emoji-name` | `DELETE` | `/api/v1/{subreddit}/emoji/{emoji_name}` | `emoji` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api delete-api-v1-subreddit-emoji-emoji-name` |
| `post-api-v1-subreddit-emoji-asset-upload-s3-json` | `POST` | `/api/v1/{subreddit}/emoji_asset_upload_s3.json` | `emoji` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api post-api-v1-subreddit-emoji-asset-upload-s3-json` |
| `post-api-v1-subreddit-emoji-custom-size` | `POST` | `/api/v1/{subreddit}/emoji_custom_size` | `emoji` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api post-api-v1-subreddit-emoji-custom-size` |
| `get-api-v1-subreddit-emojis-all` | `GET` | `/api/v1/{subreddit}/emojis/all` | `emoji` | `read` | `qwayk-reddit-safe-agent-cli api get-api-v1-subreddit-emojis-all` |
| `post-api-clearflairtemplates` | `POST` | `[/r/{subreddit}]/api/clearflairtemplates` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-clearflairtemplates` |
| `post-api-deleteflair` | `POST` | `[/r/{subreddit}]/api/deleteflair` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-deleteflair` |
| `post-api-deleteflairtemplate` | `POST` | `[/r/{subreddit}]/api/deleteflairtemplate` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-deleteflairtemplate` |
| `post-api-flair` | `POST` | `[/r/{subreddit}]/api/flair` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-flair` |
| `patch-api-flair-template-order` | `PATCH` | `[/r/{subreddit}]/api/flair_template_order` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api patch-api-flair-template-order` |
| `post-api-flairconfig` | `POST` | `[/r/{subreddit}]/api/flairconfig` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-flairconfig` |
| `post-api-flaircsv` | `POST` | `[/r/{subreddit}]/api/flaircsv` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-flaircsv` |
| `get-api-flairlist` | `GET` | `[/r/{subreddit}]/api/flairlist` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api get-api-flairlist` |
| `post-api-flairselector` | `POST` | `[/r/{subreddit}]/api/flairselector` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api post-api-flairselector` |
| `post-api-flairtemplate` | `POST` | `[/r/{subreddit}]/api/flairtemplate` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-flairtemplate` |
| `post-api-flairtemplate-v2` | `POST` | `[/r/{subreddit}]/api/flairtemplate_v2` | `flair` | `modflair` | `qwayk-reddit-safe-agent-cli api post-api-flairtemplate-v2` |
| `get-api-link-flair` | `GET` | `[/r/{subreddit}]/api/link_flair` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api get-api-link-flair` |
| `get-api-link-flair-v2` | `GET` | `[/r/{subreddit}]/api/link_flair_v2` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api get-api-link-flair-v2` |
| `post-api-selectflair` | `POST` | `[/r/{subreddit}]/api/selectflair` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api post-api-selectflair` |
| `post-api-setflairenabled` | `POST` | `[/r/{subreddit}]/api/setflairenabled` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api post-api-setflairenabled` |
| `get-api-user-flair` | `GET` | `[/r/{subreddit}]/api/user_flair` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api get-api-user-flair` |
| `get-api-user-flair-v2` | `GET` | `[/r/{subreddit}]/api/user_flair_v2` | `flair` | `flair` | `qwayk-reddit-safe-agent-cli api get-api-user-flair-v2` |
| `post-api-comment` | `POST` | `/api/comment` | `links comments` | `any` | `qwayk-reddit-safe-agent-cli api post-api-comment` |
| `post-api-del` | `POST` | `/api/del` | `links comments` | `edit` | `qwayk-reddit-safe-agent-cli api post-api-del` |
| `post-api-editusertext` | `POST` | `/api/editusertext` | `links comments` | `edit` | `qwayk-reddit-safe-agent-cli api post-api-editusertext` |
| `post-api-follow-post` | `POST` | `/api/follow_post` | `links comments` | `subscribe` | `qwayk-reddit-safe-agent-cli api post-api-follow-post` |
| `post-api-hide` | `POST` | `/api/hide` | `links comments` | `report` | `qwayk-reddit-safe-agent-cli api post-api-hide` |
| `get-api-info` | `GET` | `[/r/{subreddit}]/api/info` | `links comments` | `read` | `qwayk-reddit-safe-agent-cli api get-api-info` |
| `post-api-lock` | `POST` | `/api/lock` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-lock` |
| `post-api-marknsfw` | `POST` | `/api/marknsfw` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-marknsfw` |
| `get-api-morechildren` | `GET` | `/api/morechildren` | `links comments` | `read` | `qwayk-reddit-safe-agent-cli api get-api-morechildren` |
| `post-api-report` | `POST` | `/api/report` | `links comments` | `report` | `qwayk-reddit-safe-agent-cli api post-api-report` |
| `post-api-save` | `POST` | `/api/save` | `links comments` | `save` | `qwayk-reddit-safe-agent-cli api post-api-save` |
| `get-api-saved-categories` | `GET` | `/api/saved_categories` | `links comments` | `save` | `qwayk-reddit-safe-agent-cli api get-api-saved-categories` |
| `post-api-sendreplies` | `POST` | `/api/sendreplies` | `links comments` | `edit` | `qwayk-reddit-safe-agent-cli api post-api-sendreplies` |
| `post-api-set-contest-mode` | `POST` | `/api/set_contest_mode` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-set-contest-mode` |
| `post-api-set-subreddit-sticky` | `POST` | `/api/set_subreddit_sticky` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-set-subreddit-sticky` |
| `post-api-set-suggested-sort` | `POST` | `/api/set_suggested_sort` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-set-suggested-sort` |
| `post-api-spoiler` | `POST` | `/api/spoiler` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-spoiler` |
| `post-api-store-visits` | `POST` | `/api/store_visits` | `links comments` | `save` | `qwayk-reddit-safe-agent-cli api post-api-store-visits` |
| `post-api-submit` | `POST` | `/api/submit` | `links comments` | `submit` | `qwayk-reddit-safe-agent-cli api post-api-submit` |
| `post-api-unhide` | `POST` | `/api/unhide` | `links comments` | `report` | `qwayk-reddit-safe-agent-cli api post-api-unhide` |
| `post-api-unlock` | `POST` | `/api/unlock` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-unlock` |
| `post-api-unmarknsfw` | `POST` | `/api/unmarknsfw` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-unmarknsfw` |
| `post-api-unsave` | `POST` | `/api/unsave` | `links comments` | `save` | `qwayk-reddit-safe-agent-cli api post-api-unsave` |
| `post-api-unspoiler` | `POST` | `/api/unspoiler` | `links comments` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-unspoiler` |
| `post-api-vote` | `POST` | `/api/vote` | `links comments` | `vote` | `qwayk-reddit-safe-agent-cli api post-api-vote` |
| `get-best` | `GET` | `/best` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-best` |
| `get-by-id-names` | `GET` | `/by_id/{names}` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-by-id-names` |
| `get-comments-article` | `GET` | `[/r/{subreddit}]/comments/{article}` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-comments-article` |
| `get-duplicates-article` | `GET` | `/duplicates/{article}` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-duplicates-article` |
| `get-hot` | `GET` | `[/r/{subreddit}]/hot` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-hot` |
| `get-new` | `GET` | `[/r/{subreddit}]/new` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-new` |
| `get-rising` | `GET` | `[/r/{subreddit}]/rising` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-rising` |
| `get-top` | `GET` | `[/r/{subreddit}]/top` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-top` |
| `get-controversial` | `GET` | `[/r/{subreddit}]/controversial` | `listings` | `read` | `qwayk-reddit-safe-agent-cli api get-controversial` |
| `get-api-live-by-id-names` | `GET` | `/api/live/by_id/{names}` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-api-live-by-id-names` |
| `post-api-live-create` | `POST` | `/api/live/create` | `live threads` | `submit` | `qwayk-reddit-safe-agent-cli api post-api-live-create` |
| `get-api-live-happening-now` | `GET` | `/api/live/happening_now` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-api-live-happening-now` |
| `post-api-live-thread-accept-contributor-invite` | `POST` | `/api/live/{thread}/accept_contributor_invite` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-accept-contributor-invite` |
| `post-api-live-thread-close-thread` | `POST` | `/api/live/{thread}/close_thread` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-close-thread` |
| `post-api-live-thread-delete-update` | `POST` | `/api/live/{thread}/delete_update` | `live threads` | `edit` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-delete-update` |
| `post-api-live-thread-edit` | `POST` | `/api/live/{thread}/edit` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-edit` |
| `post-api-live-thread-hide-discussion` | `POST` | `/api/live/{thread}/hide_discussion` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-hide-discussion` |
| `post-api-live-thread-invite-contributor` | `POST` | `/api/live/{thread}/invite_contributor` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-invite-contributor` |
| `post-api-live-thread-leave-contributor` | `POST` | `/api/live/{thread}/leave_contributor` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-leave-contributor` |
| `post-api-live-thread-report` | `POST` | `/api/live/{thread}/report` | `live threads` | `report` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-report` |
| `post-api-live-thread-rm-contributor` | `POST` | `/api/live/{thread}/rm_contributor` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-rm-contributor` |
| `post-api-live-thread-rm-contributor-invite` | `POST` | `/api/live/{thread}/rm_contributor_invite` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-rm-contributor-invite` |
| `post-api-live-thread-set-contributor-permissions` | `POST` | `/api/live/{thread}/set_contributor_permissions` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-set-contributor-permissions` |
| `post-api-live-thread-strike-update` | `POST` | `/api/live/{thread}/strike_update` | `live threads` | `edit` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-strike-update` |
| `post-api-live-thread-unhide-discussion` | `POST` | `/api/live/{thread}/unhide_discussion` | `live threads` | `livemanage` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-unhide-discussion` |
| `post-api-live-thread-update` | `POST` | `/api/live/{thread}/update` | `live threads` | `submit` | `qwayk-reddit-safe-agent-cli api post-api-live-thread-update` |
| `get-live-thread` | `GET` | `/live/{thread}` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-live-thread` |
| `get-live-thread-about` | `GET` | `/live/{thread}/about` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-live-thread-about` |
| `get-live-thread-contributors` | `GET` | `/live/{thread}/contributors` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-live-thread-contributors` |
| `get-live-thread-discussions` | `GET` | `/live/{thread}/discussions` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-live-thread-discussions` |
| `get-live-thread-updates-update-id` | `GET` | `/live/{thread}/updates/{update_id}` | `live threads` | `read` | `qwayk-reddit-safe-agent-cli api get-live-thread-updates-update-id` |
| `post-api-compose` | `POST` | `/api/compose` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api post-api-compose` |
| `post-api-del-msg` | `POST` | `/api/del_msg` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api post-api-del-msg` |
| `post-api-read-all-messages` | `POST` | `/api/read_all_messages` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api post-api-read-all-messages` |
| `post-api-read-message` | `POST` | `/api/read_message` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api post-api-read-message` |
| `get-message-inbox` | `GET` | `/message/inbox` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api get-message-inbox` |
| `get-message-unread` | `GET` | `/message/unread` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api get-message-unread` |
| `get-message-sent` | `GET` | `/message/sent` | `private messages` | `privatemessages` | `qwayk-reddit-safe-agent-cli api get-message-sent` |
| `get-api-v1-scopes` | `GET` | `/api/v1/scopes` | `misc` | `any` | `qwayk-reddit-safe-agent-cli api get-api-v1-scopes` |
| `get-about-log` | `GET` | `[/r/{subreddit}]/about/log` | `moderation` | `modlog` | `qwayk-reddit-safe-agent-cli api get-about-log` |
| `get-about-reports` | `GET` | `[/r/{subreddit}]/about/reports` | `moderation` | `read` | `qwayk-reddit-safe-agent-cli api get-about-reports` |
| `get-about-spam` | `GET` | `[/r/{subreddit}]/about/spam` | `moderation` | `read` | `qwayk-reddit-safe-agent-cli api get-about-spam` |
| `get-about-modqueue` | `GET` | `[/r/{subreddit}]/about/modqueue` | `moderation` | `read` | `qwayk-reddit-safe-agent-cli api get-about-modqueue` |
| `get-about-unmoderated` | `GET` | `[/r/{subreddit}]/about/unmoderated` | `moderation` | `read` | `qwayk-reddit-safe-agent-cli api get-about-unmoderated` |
| `get-about-edited` | `GET` | `[/r/{subreddit}]/about/edited` | `moderation` | `read` | `qwayk-reddit-safe-agent-cli api get-about-edited` |
| `post-api-accept-moderator-invite` | `POST` | `[/r/{subreddit}]/api/accept_moderator_invite` | `moderation` | `modself` | `qwayk-reddit-safe-agent-cli api post-api-accept-moderator-invite` |
| `post-api-approve` | `POST` | `/api/approve` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-approve` |
| `post-api-distinguish` | `POST` | `/api/distinguish` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-distinguish` |
| `post-api-ignore-reports` | `POST` | `/api/ignore_reports` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-ignore-reports` |
| `post-api-leavecontributor` | `POST` | `/api/leavecontributor` | `moderation` | `modself` | `qwayk-reddit-safe-agent-cli api post-api-leavecontributor` |
| `post-api-leavemoderator` | `POST` | `/api/leavemoderator` | `moderation` | `modself` | `qwayk-reddit-safe-agent-cli api post-api-leavemoderator` |
| `post-api-remove` | `POST` | `/api/remove` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-remove` |
| `post-api-show-comment` | `POST` | `/api/show_comment` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-show-comment` |
| `post-api-snooze-reports` | `POST` | `/api/snooze_reports` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-snooze-reports` |
| `post-api-unignore-reports` | `POST` | `/api/unignore_reports` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-unignore-reports` |
| `post-api-unsnooze-reports` | `POST` | `/api/unsnooze_reports` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-unsnooze-reports` |
| `post-api-update-crowd-control-level` | `POST` | `/api/update_crowd_control_level` | `moderation` | `modposts` | `qwayk-reddit-safe-agent-cli api post-api-update-crowd-control-level` |
| `get-stylesheet` | `GET` | `[/r/{subreddit}]/stylesheet` | `moderation` | `modconfig` | `qwayk-reddit-safe-agent-cli api get-stylesheet` |
| `post-api-mod-bulk-read` | `POST` | `/api/mod/bulk_read` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-bulk-read` |
| `get-api-mod-conversations` | `GET` | `/api/mod/conversations` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api get-api-mod-conversations` |
| `post-api-mod-conversations` | `POST` | `/api/mod/conversations` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations` |
| `get-api-mod-conversations-conversation-id` | `GET` | `/api/mod/conversations/:conversation_id` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api get-api-mod-conversations-conversation-id` |
| `post-api-mod-conversations-conversation-id` | `POST` | `/api/mod/conversations/:conversation_id` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id` |
| `post-api-mod-conversations-conversation-id-approve` | `POST` | `/api/mod/conversations/:conversation_id/approve` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-approve` |
| `post-api-mod-conversations-conversation-id-archive` | `POST` | `/api/mod/conversations/:conversation_id/archive` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-archive` |
| `post-api-mod-conversations-conversation-id-disapprove` | `POST` | `/api/mod/conversations/:conversation_id/disapprove` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-disapprove` |
| `delete-api-mod-conversations-conversation-id-highlight` | `DELETE` | `/api/mod/conversations/:conversation_id/highlight` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api delete-api-mod-conversations-conversation-id-highlight` |
| `post-api-mod-conversations-conversation-id-highlight` | `POST` | `/api/mod/conversations/:conversation_id/highlight` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-highlight` |
| `post-api-mod-conversations-conversation-id-mute` | `POST` | `/api/mod/conversations/:conversation_id/mute` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-mute` |
| `post-api-mod-conversations-conversation-id-temp-ban` | `POST` | `/api/mod/conversations/:conversation_id/temp_ban` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-temp-ban` |
| `post-api-mod-conversations-conversation-id-unarchive` | `POST` | `/api/mod/conversations/:conversation_id/unarchive` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-unarchive` |
| `post-api-mod-conversations-conversation-id-unban` | `POST` | `/api/mod/conversations/:conversation_id/unban` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-unban` |
| `post-api-mod-conversations-conversation-id-unmute` | `POST` | `/api/mod/conversations/:conversation_id/unmute` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-conversation-id-unmute` |
| `post-api-mod-conversations-read` | `POST` | `/api/mod/conversations/read` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-read` |
| `get-api-mod-conversations-subreddits` | `GET` | `/api/mod/conversations/subreddits` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api get-api-mod-conversations-subreddits` |
| `post-api-mod-conversations-unread` | `POST` | `/api/mod/conversations/unread` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api post-api-mod-conversations-unread` |
| `get-api-mod-conversations-unread-count` | `GET` | `/api/mod/conversations/unread/count` | `new modmail` | `modmail` | `qwayk-reddit-safe-agent-cli api get-api-mod-conversations-unread-count` |
| `delete-api-mod-notes` | `DELETE` | `/api/mod/notes` | `modnote` | `modnote` | `qwayk-reddit-safe-agent-cli api delete-api-mod-notes` |
| `get-api-mod-notes` | `GET` | `/api/mod/notes` | `modnote` | `modnote` | `qwayk-reddit-safe-agent-cli api get-api-mod-notes` |
| `post-api-mod-notes` | `POST` | `/api/mod/notes` | `modnote` | `modnote` | `qwayk-reddit-safe-agent-cli api post-api-mod-notes` |
| `get-api-mod-notes-recent` | `GET` | `/api/mod/notes/recent` | `modnote` | `modnote` | `qwayk-reddit-safe-agent-cli api get-api-mod-notes-recent` |
| `post-api-multi-copy` | `POST` | `/api/multi/copy` | `multis` | `subscribe` | `qwayk-reddit-safe-agent-cli api post-api-multi-copy` |
| `get-api-multi-mine` | `GET` | `/api/multi/mine` | `multis` | `read` | `qwayk-reddit-safe-agent-cli api get-api-multi-mine` |
| `get-api-multi-user-username` | `GET` | `/api/multi/user/{username}` | `multis` | `read` | `qwayk-reddit-safe-agent-cli api get-api-multi-user-username` |
| `delete-api-filter-filterpath` | `DELETE` | `/api/filter/{filterpath}` | `multis` | `subscribe` | `qwayk-reddit-safe-agent-cli api delete-api-filter-filterpath` |
| `get-api-filter-filterpath` | `GET` | `/api/filter/{filterpath}` | `multis` | `read` | `qwayk-reddit-safe-agent-cli api get-api-filter-filterpath` |
| `post-api-filter-filterpath` | `POST` | `/api/filter/{filterpath}` | `multis` | `subscribe` | `qwayk-reddit-safe-agent-cli api post-api-filter-filterpath` |
| `put-api-filter-filterpath` | `PUT` | `/api/filter/{filterpath}` | `multis` | `subscribe` | `qwayk-reddit-safe-agent-cli api put-api-filter-filterpath` |
| `get-api-multi-multipath-description` | `GET` | `/api/multi/{multipath}/description` | `multis` | `read` | `qwayk-reddit-safe-agent-cli api get-api-multi-multipath-description` |
| `put-api-multi-multipath-description` | `PUT` | `/api/multi/{multipath}/description` | `multis` | `read` | `qwayk-reddit-safe-agent-cli api put-api-multi-multipath-description` |
| `delete-api-filter-filterpath-r-srname` | `DELETE` | `/api/filter/{filterpath}/r/{srname}` | `multis` | `subscribe` | `qwayk-reddit-safe-agent-cli api delete-api-filter-filterpath-r-srname` |
| `get-api-filter-filterpath-r-srname` | `GET` | `/api/filter/{filterpath}/r/{srname}` | `multis` | `read` | `qwayk-reddit-safe-agent-cli api get-api-filter-filterpath-r-srname` |
| `put-api-filter-filterpath-r-srname` | `PUT` | `/api/filter/{filterpath}/r/{srname}` | `multis` | `subscribe` | `qwayk-reddit-safe-agent-cli api put-api-filter-filterpath-r-srname` |
| `get-search` | `GET` | `[/r/{subreddit}]/search` | `search` | `read` | `qwayk-reddit-safe-agent-cli api get-search` |
| `get-about-banned` | `GET` | `[/r/{subreddit}]/about/banned` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-about-banned` |
| `get-about-muted` | `GET` | `[/r/{subreddit}]/about/muted` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-about-muted` |
| `get-about-wikibanned` | `GET` | `[/r/{subreddit}]/about/wikibanned` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-about-wikibanned` |
| `get-about-contributors` | `GET` | `[/r/{subreddit}]/about/contributors` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-about-contributors` |
| `get-about-wikicontributors` | `GET` | `[/r/{subreddit}]/about/wikicontributors` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-about-wikicontributors` |
| `get-about-moderators` | `GET` | `[/r/{subreddit}]/about/moderators` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-about-moderators` |
| `post-api-delete-sr-banner` | `POST` | `[/r/{subreddit}]/api/delete_sr_banner` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-delete-sr-banner` |
| `post-api-delete-sr-header` | `POST` | `[/r/{subreddit}]/api/delete_sr_header` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-delete-sr-header` |
| `post-api-delete-sr-icon` | `POST` | `[/r/{subreddit}]/api/delete_sr_icon` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-delete-sr-icon` |
| `post-api-delete-sr-img` | `POST` | `[/r/{subreddit}]/api/delete_sr_img` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-delete-sr-img` |
| `get-api-recommend-sr-srnames` | `GET` | `/api/recommend/sr/{srnames}` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-api-recommend-sr-srnames` |
| `get-api-search-reddit-names` | `GET` | `/api/search_reddit_names` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-api-search-reddit-names` |
| `post-api-search-reddit-names` | `POST` | `/api/search_reddit_names` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api post-api-search-reddit-names` |
| `post-api-search-subreddits` | `POST` | `/api/search_subreddits` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api post-api-search-subreddits` |
| `post-api-site-admin` | `POST` | `/api/site_admin` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-site-admin` |
| `get-api-submit-text` | `GET` | `[/r/{subreddit}]/api/submit_text` | `subreddits` | `submit` | `qwayk-reddit-safe-agent-cli api get-api-submit-text` |
| `get-api-subreddit-autocomplete` | `GET` | `/api/subreddit_autocomplete` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-api-subreddit-autocomplete` |
| `get-api-subreddit-autocomplete-v2` | `GET` | `/api/subreddit_autocomplete_v2` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-api-subreddit-autocomplete-v2` |
| `post-api-subreddit-stylesheet` | `POST` | `[/r/{subreddit}]/api/subreddit_stylesheet` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-subreddit-stylesheet` |
| `post-api-subscribe` | `POST` | `/api/subscribe` | `subreddits` | `subscribe` | `qwayk-reddit-safe-agent-cli api post-api-subscribe` |
| `post-api-upload-sr-img` | `POST` | `[/r/{subreddit}]/api/upload_sr_img` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api post-api-upload-sr-img` |
| `get-api-v1-subreddit-post-requirements` | `GET` | `/api/v1/{subreddit}/post_requirements` | `subreddits` | `submit` | `qwayk-reddit-safe-agent-cli api get-api-v1-subreddit-post-requirements` |
| `get-r-subreddit-about` | `GET` | `/r/{subreddit}/about` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-r-subreddit-about` |
| `get-r-subreddit-about-edit` | `GET` | `/r/{subreddit}/about/edit` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api get-r-subreddit-about-edit` |
| `get-r-subreddit-about-rules` | `GET` | `/r/{subreddit}/about/rules` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-r-subreddit-about-rules` |
| `get-r-subreddit-about-traffic` | `GET` | `/r/{subreddit}/about/traffic` | `subreddits` | `modconfig` | `qwayk-reddit-safe-agent-cli api get-r-subreddit-about-traffic` |
| `get-sidebar` | `GET` | `[/r/{subreddit}]/sidebar` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-sidebar` |
| `get-sticky` | `GET` | `[/r/{subreddit}]/sticky` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-sticky` |
| `get-subreddits-mine-subscriber` | `GET` | `/subreddits/mine/subscriber` | `subreddits` | `mysubreddits` | `qwayk-reddit-safe-agent-cli api get-subreddits-mine-subscriber` |
| `get-subreddits-mine-contributor` | `GET` | `/subreddits/mine/contributor` | `subreddits` | `mysubreddits` | `qwayk-reddit-safe-agent-cli api get-subreddits-mine-contributor` |
| `get-subreddits-mine-moderator` | `GET` | `/subreddits/mine/moderator` | `subreddits` | `mysubreddits` | `qwayk-reddit-safe-agent-cli api get-subreddits-mine-moderator` |
| `get-subreddits-mine-streams` | `GET` | `/subreddits/mine/streams` | `subreddits` | `mysubreddits` | `qwayk-reddit-safe-agent-cli api get-subreddits-mine-streams` |
| `get-subreddits-search` | `GET` | `/subreddits/search` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-subreddits-search` |
| `get-subreddits-popular` | `GET` | `/subreddits/popular` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-subreddits-popular` |
| `get-subreddits-new` | `GET` | `/subreddits/new` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-subreddits-new` |
| `get-subreddits-gold` | `GET` | `/subreddits/gold` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-subreddits-gold` |
| `get-subreddits-default` | `GET` | `/subreddits/default` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-subreddits-default` |
| `get-users-search` | `GET` | `/users/search` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-users-search` |
| `get-users-popular` | `GET` | `/users/popular` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-users-popular` |
| `get-users-new` | `GET` | `/users/new` | `subreddits` | `read` | `qwayk-reddit-safe-agent-cli api get-users-new` |
| `post-api-block-user` | `POST` | `/api/block_user` | `users` | `account` | `qwayk-reddit-safe-agent-cli api post-api-block-user` |
| `post-api-friend` | `POST` | `[/r/{subreddit}]/api/friend` | `users` | `any` | `qwayk-reddit-safe-agent-cli api post-api-friend` |
| `post-api-report-user` | `POST` | `/api/report_user` | `users` | `report` | `qwayk-reddit-safe-agent-cli api post-api-report-user` |
| `post-api-setpermissions` | `POST` | `[/r/{subreddit}]/api/setpermissions` | `users` | `modothers` | `qwayk-reddit-safe-agent-cli api post-api-setpermissions` |
| `post-api-unfriend` | `POST` | `[/r/{subreddit}]/api/unfriend` | `users` | `any` | `qwayk-reddit-safe-agent-cli api post-api-unfriend` |
| `get-api-user-data-by-account-ids` | `GET` | `/api/user_data_by_account_ids` | `users` | `privatemessages` | `qwayk-reddit-safe-agent-cli api get-api-user-data-by-account-ids` |
| `get-api-username-available` | `GET` | `/api/username_available` | `users` | `any` | `qwayk-reddit-safe-agent-cli api get-api-username-available` |
| `delete-api-v1-me-friends-username` | `DELETE` | `/api/v1/me/friends/{username}` | `users` | `subscribe` | `qwayk-reddit-safe-agent-cli api delete-api-v1-me-friends-username` |
| `put-api-v1-me-friends-username` | `PUT` | `/api/v1/me/friends/{username}` | `users` | `subscribe` | `qwayk-reddit-safe-agent-cli api put-api-v1-me-friends-username` |
| `get-api-v1-user-username-trophies` | `GET` | `/api/v1/user/{username}/trophies` | `users` | `read` | `qwayk-reddit-safe-agent-cli api get-api-v1-user-username-trophies` |
| `get-user-username-about` | `GET` | `/user/{username}/about` | `users` | `read` | `qwayk-reddit-safe-agent-cli api get-user-username-about` |
| `get-user-username-overview` | `GET` | `/user/{username}/overview` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-overview` |
| `get-user-username-submitted` | `GET` | `/user/{username}/submitted` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-submitted` |
| `get-user-username-comments` | `GET` | `/user/{username}/comments` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-comments` |
| `get-user-username-upvoted` | `GET` | `/user/{username}/upvoted` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-upvoted` |
| `get-user-username-downvoted` | `GET` | `/user/{username}/downvoted` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-downvoted` |
| `get-user-username-hidden` | `GET` | `/user/{username}/hidden` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-hidden` |
| `get-user-username-saved` | `GET` | `/user/{username}/saved` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-saved` |
| `get-user-username-gilded` | `GET` | `/user/{username}/gilded` | `users` | `history` | `qwayk-reddit-safe-agent-cli api get-user-username-gilded` |
| `post-api-widget` | `POST` | `[/r/{subreddit}]/api/widget` | `widgets` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api post-api-widget` |
| `delete-api-widget-widget-id` | `DELETE` | `[/r/{subreddit}]/api/widget/{widget_id}` | `widgets` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api delete-api-widget-widget-id` |
| `put-api-widget-widget-id` | `PUT` | `[/r/{subreddit}]/api/widget/{widget_id}` | `widgets` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api put-api-widget-widget-id` |
| `post-api-widget-image-upload-s3` | `POST` | `[/r/{subreddit}]/api/widget_image_upload_s3` | `widgets` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api post-api-widget-image-upload-s3` |
| `patch-api-widget-order-section` | `PATCH` | `[/r/{subreddit}]/api/widget_order/{section}` | `widgets` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api patch-api-widget-order-section` |
| `get-api-widgets` | `GET` | `[/r/{subreddit}]/api/widgets` | `widgets` | `structuredstyles` | `qwayk-reddit-safe-agent-cli api get-api-widgets` |
| `post-api-wiki-alloweditor-del` | `POST` | `[/r/{subreddit}]/api/wiki/alloweditor/del` | `wiki` | `modwiki` | `qwayk-reddit-safe-agent-cli api post-api-wiki-alloweditor-del` |
| `post-api-wiki-alloweditor-add` | `POST` | `[/r/{subreddit}]/api/wiki/alloweditor/add` | `wiki` | `modwiki` | `qwayk-reddit-safe-agent-cli api post-api-wiki-alloweditor-add` |
| `post-api-wiki-edit` | `POST` | `[/r/{subreddit}]/api/wiki/edit` | `wiki` | `wikiedit` | `qwayk-reddit-safe-agent-cli api post-api-wiki-edit` |
| `post-api-wiki-hide` | `POST` | `[/r/{subreddit}]/api/wiki/hide` | `wiki` | `modwiki` | `qwayk-reddit-safe-agent-cli api post-api-wiki-hide` |
| `post-api-wiki-revert` | `POST` | `[/r/{subreddit}]/api/wiki/revert` | `wiki` | `modwiki` | `qwayk-reddit-safe-agent-cli api post-api-wiki-revert` |
| `get-wiki-discussions-page` | `GET` | `[/r/{subreddit}]/wiki/discussions/{page}` | `wiki` | `wikiread` | `qwayk-reddit-safe-agent-cli api get-wiki-discussions-page` |
| `get-wiki-pages` | `GET` | `[/r/{subreddit}]/wiki/pages` | `wiki` | `wikiread` | `qwayk-reddit-safe-agent-cli api get-wiki-pages` |
| `get-wiki-revisions` | `GET` | `[/r/{subreddit}]/wiki/revisions` | `wiki` | `wikiread` | `qwayk-reddit-safe-agent-cli api get-wiki-revisions` |
| `get-wiki-revisions-page` | `GET` | `[/r/{subreddit}]/wiki/revisions/{page}` | `wiki` | `wikiread` | `qwayk-reddit-safe-agent-cli api get-wiki-revisions-page` |
| `get-wiki-settings-page` | `GET` | `[/r/{subreddit}]/wiki/settings/{page}` | `wiki` | `modwiki` | `qwayk-reddit-safe-agent-cli api get-wiki-settings-page` |
| `post-wiki-settings-page` | `POST` | `[/r/{subreddit}]/wiki/settings/{page}` | `wiki` | `modwiki` | `qwayk-reddit-safe-agent-cli api post-wiki-settings-page` |
| `get-wiki-page` | `GET` | `[/r/{subreddit}]/wiki/{page}` | `wiki` | `wikiread` | `qwayk-reddit-safe-agent-cli api get-wiki-page` |

## Known gaps

- None in the pinned inventory file. Runtime support still needs live access approval and OAuth setup.

## Notes

- Optional subreddit prefixes are shown in square brackets, for example `[/r/{subreddit}]/new`.
- Deprecated or policy-limited endpoints stay in scope if they are still listed in the official docs snapshot.
