# Instagram Login Tool References

Last verified (UTC): 2026-05-22

## Official Meta docs

- Instagram Platform home: `https://developers.facebook.com/docs/instagram-platform/`
- Instagram Platform overview: `https://developers.facebook.com/docs/instagram-platform/overview`
- Instagram API with Instagram Login overview: `https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/`
- Business Login for Instagram: `https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/business-login`
- Create a Meta app for Instagram Platform: `https://developers.facebook.com/docs/instagram-platform/create-an-instagram-app`
- Content publishing guide: `https://developers.facebook.com/docs/instagram-platform/content-publishing/`
- Comment moderation guide: `https://developers.facebook.com/docs/instagram-platform/comment-moderation/`
- Private replies guide: `https://developers.facebook.com/docs/instagram-platform/private-replies/`
- Messaging guide: `https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api`
- Insights guide: `https://developers.facebook.com/docs/instagram-platform/insights/`
- Webhooks guide: `https://developers.facebook.com/docs/instagram-platform/webhooks/`
- Changelog: `https://developers.facebook.com/docs/instagram-platform/changelog/`

## Official reference pages used for command mapping

- `IG User`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/`
- `IG User Media`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/media`
- `IG User Media Publish`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/media_publish`
- `IG User Content Publishing Limit`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/content_publishing_limit`
- `IG User Insights`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights`
- `IG User Tags`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/tags`
- `IG User Stories`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories`
- `IG User Live Media`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/live_media`
- `IG User Mentions`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/mentions`
- `IG User Mentioned Media`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/mentioned_media`
- `IG User Mentioned Comment`: `https://developers.facebook.com/docs/instagram-api/reference/ig-user/mentioned_comment`
- `IG Media`: `https://developers.facebook.com/docs/instagram-api/reference/ig-media`
- `IG Media Comments`: `https://developers.facebook.com/docs/instagram-api/reference/ig-media/comments`
- `IG Media Insights`: `https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights`
- `IG Media Children`: `https://developers.facebook.com/docs/instagram-api/reference/ig-media/children`
- `IG Comment`: `https://developers.facebook.com/docs/instagram-api/reference/ig-comment`
- `IG Comment Replies`: `https://developers.facebook.com/docs/instagram-api/reference/ig-comment/replies`
- `IG Container`: `https://developers.facebook.com/docs/instagram-api/reference/ig-container`
- `/me`: `https://developers.facebook.com/docs/instagram-platform/reference/me`
- `/access_token`: `https://developers.facebook.com/docs/instagram-platform/reference/access_token`
- `/refresh_access_token`: `https://developers.facebook.com/docs/instagram-platform/reference/refresh_access_token`

## Official excluded-scope references

- Business Discovery: `https://developers.facebook.com/docs/instagram-api/guides/business-discovery`
- Hashtag Search: `https://developers.facebook.com/docs/instagram-api/guides/hashtag-search`
- `IG Hashtag`: `https://developers.facebook.com/docs/instagram-api/reference/ig-hashtag`
- `Page` to `instagram_business_account`: `https://developers.facebook.com/docs/instagram-api/reference/page`
- `IG Media Product Tags`: `https://developers.facebook.com/docs/instagram-api/reference/ig-media/product_tags`
- `IG User connected_threads_user`: `https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/connected_threads_user`
- `IG User instagram_backed_threads_user`: `https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/instagram_backed_threads_user`

## Notes

- The official docs currently mix `graph.instagram.com` and `graph.facebook.com` examples across older reference pages. This tool follows the Instagram Login product docs and treats `graph.instagram.com` as the primary host for shipped Instagram Login commands unless a command family is explicitly documented otherwise.
- Some `IG User` edges are listed in the main reference table but their public static detail pages were not retrievable on 2026-05-22. Those are tracked in `docs/api_coverage.md` as reference gaps, not shipped commands.
