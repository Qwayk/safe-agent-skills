# API coverage (Bluesky / atproto XRPC surface)

Purpose:
- Make official Bluesky API coverage measurable.
- Keep every callable official lexicon tied to an explicit CLI subcommand.
- Keep record lexicons honest: they are not fake extra endpoints; they are used through `com.atproto.repo.*` methods.

## Summary

- Provider: Bluesky / atproto lexicon APIs
- Product shape: one official XRPC API world, not split products
- Primary auth path: handle or DID plus app password via `com.atproto.server.createSession`, then authenticated calls via the user's PDS
- Public read option: `https://public.api.bsky.app` for public Bluesky AppView reads
- Official HTTP reference pages: 222
- Official callable lexicons: 304
- Lexicon-only rows: 82
- Last audited (UTC): 2026-05-25

Namespace totals:
- `app.bsky`: 111
- `chat.bsky`: 42
- `com.atproto`: 86
- `tools.ozone`: 65

Stability notes:
- `unspecced` rows are official but intentionally not part of the stable public contract.
- `temp` rows are official temporary lexicons and should be treated as unstable.
- `active-development` rows are official lexicons whose descriptions explicitly warn they are under active development.

Coverage rule for this tool:
- Every row below must be reachable as an explicit subcommand under `bluesky-safe-cli api <operation_command>`.
- No raw request bridge counts toward coverage.

## Inventory mapping

| operation_command | lexicon_id | kind | route_hint | docs_source | stability | primary_cli |
|---|---|---|---|---|---|---|
| `app-bsky-actor-get-preferences` | `app.bsky.actor.getPreferences` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-get-preferences` |
| `app-bsky-actor-get-profile` | `app.bsky.actor.getProfile` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-get-profile` |
| `app-bsky-actor-get-profiles` | `app.bsky.actor.getProfiles` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-get-profiles` |
| `app-bsky-actor-get-suggestions` | `app.bsky.actor.getSuggestions` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-get-suggestions` |
| `app-bsky-actor-put-preferences` | `app.bsky.actor.putPreferences` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-put-preferences` |
| `app-bsky-actor-search-actors` | `app.bsky.actor.searchActors` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-search-actors` |
| `app-bsky-actor-search-actors-typeahead` | `app.bsky.actor.searchActorsTypeahead` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-actor-search-actors-typeahead` |
| `app-bsky-ageassurance-begin` | `app.bsky.ageassurance.begin` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-ageassurance-begin` |
| `app-bsky-ageassurance-get-config` | `app.bsky.ageassurance.getConfig` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-ageassurance-get-config` |
| `app-bsky-ageassurance-get-state` | `app.bsky.ageassurance.getState` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-ageassurance-get-state` |
| `app-bsky-bookmark-create-bookmark` | `app.bsky.bookmark.createBookmark` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-bookmark-create-bookmark` |
| `app-bsky-bookmark-delete-bookmark` | `app.bsky.bookmark.deleteBookmark` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-bookmark-delete-bookmark` |
| `app-bsky-bookmark-get-bookmarks` | `app.bsky.bookmark.getBookmarks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-bookmark-get-bookmarks` |
| `app-bsky-contact-dismiss-match` | `app.bsky.contact.dismissMatch` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-dismiss-match` |
| `app-bsky-contact-get-matches` | `app.bsky.contact.getMatches` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-get-matches` |
| `app-bsky-contact-get-sync-status` | `app.bsky.contact.getSyncStatus` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-get-sync-status` |
| `app-bsky-contact-import-contacts` | `app.bsky.contact.importContacts` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-import-contacts` |
| `app-bsky-contact-remove-data` | `app.bsky.contact.removeData` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-remove-data` |
| `app-bsky-contact-send-notification` | `app.bsky.contact.sendNotification` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-send-notification` |
| `app-bsky-contact-start-phone-verification` | `app.bsky.contact.startPhoneVerification` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-start-phone-verification` |
| `app-bsky-contact-verify-phone` | `app.bsky.contact.verifyPhone` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-contact-verify-phone` |
| `app-bsky-draft-create-draft` | `app.bsky.draft.createDraft` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-draft-create-draft` |
| `app-bsky-draft-delete-draft` | `app.bsky.draft.deleteDraft` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-draft-delete-draft` |
| `app-bsky-draft-get-drafts` | `app.bsky.draft.getDrafts` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-draft-get-drafts` |
| `app-bsky-draft-update-draft` | `app.bsky.draft.updateDraft` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-draft-update-draft` |
| `app-bsky-embed-get-embed-external-view` | `app.bsky.embed.getEmbedExternalView` | `query` | `entryway-or-pds` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api app-bsky-embed-get-embed-external-view` |
| `app-bsky-feed-describe-feed-generator` | `app.bsky.feed.describeFeedGenerator` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-describe-feed-generator` |
| `app-bsky-feed-get-actor-feeds` | `app.bsky.feed.getActorFeeds` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-actor-feeds` |
| `app-bsky-feed-get-actor-likes` | `app.bsky.feed.getActorLikes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-actor-likes` |
| `app-bsky-feed-get-author-feed` | `app.bsky.feed.getAuthorFeed` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-author-feed` |
| `app-bsky-feed-get-feed` | `app.bsky.feed.getFeed` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-feed` |
| `app-bsky-feed-get-feed-generator` | `app.bsky.feed.getFeedGenerator` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-feed-generator` |
| `app-bsky-feed-get-feed-generators` | `app.bsky.feed.getFeedGenerators` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-feed-generators` |
| `app-bsky-feed-get-feed-skeleton` | `app.bsky.feed.getFeedSkeleton` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-feed-skeleton` |
| `app-bsky-feed-get-likes` | `app.bsky.feed.getLikes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-likes` |
| `app-bsky-feed-get-list-feed` | `app.bsky.feed.getListFeed` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-list-feed` |
| `app-bsky-feed-get-post-thread` | `app.bsky.feed.getPostThread` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-post-thread` |
| `app-bsky-feed-get-posts` | `app.bsky.feed.getPosts` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-posts` |
| `app-bsky-feed-get-quotes` | `app.bsky.feed.getQuotes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-quotes` |
| `app-bsky-feed-get-reposted-by` | `app.bsky.feed.getRepostedBy` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-reposted-by` |
| `app-bsky-feed-get-suggested-feeds` | `app.bsky.feed.getSuggestedFeeds` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-suggested-feeds` |
| `app-bsky-feed-get-timeline` | `app.bsky.feed.getTimeline` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-get-timeline` |
| `app-bsky-feed-search-posts` | `app.bsky.feed.searchPosts` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-search-posts` |
| `app-bsky-feed-send-interactions` | `app.bsky.feed.sendInteractions` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-feed-send-interactions` |
| `app-bsky-graph-get-actor-starter-packs` | `app.bsky.graph.getActorStarterPacks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-actor-starter-packs` |
| `app-bsky-graph-get-blocks` | `app.bsky.graph.getBlocks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-blocks` |
| `app-bsky-graph-get-followers` | `app.bsky.graph.getFollowers` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-followers` |
| `app-bsky-graph-get-follows` | `app.bsky.graph.getFollows` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-follows` |
| `app-bsky-graph-get-known-followers` | `app.bsky.graph.getKnownFollowers` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-known-followers` |
| `app-bsky-graph-get-list` | `app.bsky.graph.getList` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-list` |
| `app-bsky-graph-get-list-blocks` | `app.bsky.graph.getListBlocks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-list-blocks` |
| `app-bsky-graph-get-list-mutes` | `app.bsky.graph.getListMutes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-list-mutes` |
| `app-bsky-graph-get-lists` | `app.bsky.graph.getLists` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-lists` |
| `app-bsky-graph-get-lists-with-membership` | `app.bsky.graph.getListsWithMembership` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-lists-with-membership` |
| `app-bsky-graph-get-mutes` | `app.bsky.graph.getMutes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-mutes` |
| `app-bsky-graph-get-relationships` | `app.bsky.graph.getRelationships` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-relationships` |
| `app-bsky-graph-get-starter-pack` | `app.bsky.graph.getStarterPack` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-starter-pack` |
| `app-bsky-graph-get-starter-packs` | `app.bsky.graph.getStarterPacks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-starter-packs` |
| `app-bsky-graph-get-starter-packs-with-membership` | `app.bsky.graph.getStarterPacksWithMembership` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-starter-packs-with-membership` |
| `app-bsky-graph-get-suggested-follows-by-actor` | `app.bsky.graph.getSuggestedFollowsByActor` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-get-suggested-follows-by-actor` |
| `app-bsky-graph-mute-actor` | `app.bsky.graph.muteActor` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-mute-actor` |
| `app-bsky-graph-mute-actor-list` | `app.bsky.graph.muteActorList` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-mute-actor-list` |
| `app-bsky-graph-mute-thread` | `app.bsky.graph.muteThread` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-mute-thread` |
| `app-bsky-graph-search-starter-packs` | `app.bsky.graph.searchStarterPacks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-search-starter-packs` |
| `app-bsky-graph-unmute-actor` | `app.bsky.graph.unmuteActor` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-unmute-actor` |
| `app-bsky-graph-unmute-actor-list` | `app.bsky.graph.unmuteActorList` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-unmute-actor-list` |
| `app-bsky-graph-unmute-thread` | `app.bsky.graph.unmuteThread` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-graph-unmute-thread` |
| `app-bsky-labeler-get-services` | `app.bsky.labeler.getServices` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-labeler-get-services` |
| `app-bsky-notification-get-preferences` | `app.bsky.notification.getPreferences` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-get-preferences` |
| `app-bsky-notification-get-unread-count` | `app.bsky.notification.getUnreadCount` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-get-unread-count` |
| `app-bsky-notification-list-activity-subscriptions` | `app.bsky.notification.listActivitySubscriptions` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-list-activity-subscriptions` |
| `app-bsky-notification-list-notifications` | `app.bsky.notification.listNotifications` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-list-notifications` |
| `app-bsky-notification-put-activity-subscription` | `app.bsky.notification.putActivitySubscription` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-put-activity-subscription` |
| `app-bsky-notification-put-preferences` | `app.bsky.notification.putPreferences` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-put-preferences` |
| `app-bsky-notification-put-preferences-v-2` | `app.bsky.notification.putPreferencesV2` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-put-preferences-v-2` |
| `app-bsky-notification-register-push` | `app.bsky.notification.registerPush` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-register-push` |
| `app-bsky-notification-unregister-push` | `app.bsky.notification.unregisterPush` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-unregister-push` |
| `app-bsky-notification-update-seen` | `app.bsky.notification.updateSeen` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-notification-update-seen` |
| `app-bsky-unspecced-get-age-assurance-state` | `app.bsky.unspecced.getAgeAssuranceState` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-age-assurance-state` |
| `app-bsky-unspecced-get-config` | `app.bsky.unspecced.getConfig` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-config` |
| `app-bsky-unspecced-get-onboarding-suggested-starter-packs` | `app.bsky.unspecced.getOnboardingSuggestedStarterPacks` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-onboarding-suggested-starter-packs` |
| `app-bsky-unspecced-get-onboarding-suggested-starter-packs-skeleton` | `app.bsky.unspecced.getOnboardingSuggestedStarterPacksSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-onboarding-suggested-starter-packs-skeleton` |
| `app-bsky-unspecced-get-onboarding-suggested-users-skeleton` | `app.bsky.unspecced.getOnboardingSuggestedUsersSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-onboarding-suggested-users-skeleton` |
| `app-bsky-unspecced-get-popular-feed-generators` | `app.bsky.unspecced.getPopularFeedGenerators` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-popular-feed-generators` |
| `app-bsky-unspecced-get-post-thread-other-v-2` | `app.bsky.unspecced.getPostThreadOtherV2` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-post-thread-other-v-2` |
| `app-bsky-unspecced-get-post-thread-v-2` | `app.bsky.unspecced.getPostThreadV2` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-post-thread-v-2` |
| `app-bsky-unspecced-get-suggested-feeds` | `app.bsky.unspecced.getSuggestedFeeds` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-feeds` |
| `app-bsky-unspecced-get-suggested-feeds-skeleton` | `app.bsky.unspecced.getSuggestedFeedsSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-feeds-skeleton` |
| `app-bsky-unspecced-get-suggested-onboarding-users` | `app.bsky.unspecced.getSuggestedOnboardingUsers` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-onboarding-users` |
| `app-bsky-unspecced-get-suggested-starter-packs` | `app.bsky.unspecced.getSuggestedStarterPacks` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-starter-packs` |
| `app-bsky-unspecced-get-suggested-starter-packs-skeleton` | `app.bsky.unspecced.getSuggestedStarterPacksSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-starter-packs-skeleton` |
| `app-bsky-unspecced-get-suggested-users` | `app.bsky.unspecced.getSuggestedUsers` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users` |
| `app-bsky-unspecced-get-suggested-users-for-discover` | `app.bsky.unspecced.getSuggestedUsersForDiscover` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-for-discover` |
| `app-bsky-unspecced-get-suggested-users-for-discover-skeleton` | `app.bsky.unspecced.getSuggestedUsersForDiscoverSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-for-discover-skeleton` |
| `app-bsky-unspecced-get-suggested-users-for-explore` | `app.bsky.unspecced.getSuggestedUsersForExplore` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-for-explore` |
| `app-bsky-unspecced-get-suggested-users-for-explore-skeleton` | `app.bsky.unspecced.getSuggestedUsersForExploreSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-for-explore-skeleton` |
| `app-bsky-unspecced-get-suggested-users-for-see-more` | `app.bsky.unspecced.getSuggestedUsersForSeeMore` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-for-see-more` |
| `app-bsky-unspecced-get-suggested-users-for-see-more-skeleton` | `app.bsky.unspecced.getSuggestedUsersForSeeMoreSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-for-see-more-skeleton` |
| `app-bsky-unspecced-get-suggested-users-skeleton` | `app.bsky.unspecced.getSuggestedUsersSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggested-users-skeleton` |
| `app-bsky-unspecced-get-suggestions-skeleton` | `app.bsky.unspecced.getSuggestionsSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-suggestions-skeleton` |
| `app-bsky-unspecced-get-tagged-suggestions` | `app.bsky.unspecced.getTaggedSuggestions` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-tagged-suggestions` |
| `app-bsky-unspecced-get-trending-topics` | `app.bsky.unspecced.getTrendingTopics` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-trending-topics` |
| `app-bsky-unspecced-get-trends` | `app.bsky.unspecced.getTrends` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-trends` |
| `app-bsky-unspecced-get-trends-skeleton` | `app.bsky.unspecced.getTrendsSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-get-trends-skeleton` |
| `app-bsky-unspecced-init-age-assurance` | `app.bsky.unspecced.initAgeAssurance` | `procedure` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-init-age-assurance` |
| `app-bsky-unspecced-search-actors-skeleton` | `app.bsky.unspecced.searchActorsSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-search-actors-skeleton` |
| `app-bsky-unspecced-search-posts-skeleton` | `app.bsky.unspecced.searchPostsSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-search-posts-skeleton` |
| `app-bsky-unspecced-search-starter-packs-skeleton` | `app.bsky.unspecced.searchStarterPacksSkeleton` | `query` | `entryway-or-pds` | `lexicon-only` | `unspecced` | `bluesky-safe-cli api app-bsky-unspecced-search-starter-packs-skeleton` |
| `app-bsky-video-get-job-status` | `app.bsky.video.getJobStatus` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-video-get-job-status` |
| `app-bsky-video-get-upload-limits` | `app.bsky.video.getUploadLimits` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-video-get-upload-limits` |
| `app-bsky-video-upload-video` | `app.bsky.video.uploadVideo` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api app-bsky-video-upload-video` |
| `chat-bsky-actor-delete-account` | `chat.bsky.actor.deleteAccount` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-actor-delete-account` |
| `chat-bsky-actor-export-account-data` | `chat.bsky.actor.exportAccountData` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-actor-export-account-data` |
| `chat-bsky-actor-get-status` | `chat.bsky.actor.getStatus` | `query` | `chat` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api chat-bsky-actor-get-status` |
| `chat-bsky-convo-accept-convo` | `chat.bsky.convo.acceptConvo` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-accept-convo` |
| `chat-bsky-convo-add-reaction` | `chat.bsky.convo.addReaction` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-add-reaction` |
| `chat-bsky-convo-delete-message-for-self` | `chat.bsky.convo.deleteMessageForSelf` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-delete-message-for-self` |
| `chat-bsky-convo-get-convo` | `chat.bsky.convo.getConvo` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-get-convo` |
| `chat-bsky-convo-get-convo-availability` | `chat.bsky.convo.getConvoAvailability` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-get-convo-availability` |
| `chat-bsky-convo-get-convo-for-members` | `chat.bsky.convo.getConvoForMembers` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-get-convo-for-members` |
| `chat-bsky-convo-get-convo-members` | `chat.bsky.convo.getConvoMembers` | `query` | `chat` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api chat-bsky-convo-get-convo-members` |
| `chat-bsky-convo-get-log` | `chat.bsky.convo.getLog` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-get-log` |
| `chat-bsky-convo-get-messages` | `chat.bsky.convo.getMessages` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-get-messages` |
| `chat-bsky-convo-leave-convo` | `chat.bsky.convo.leaveConvo` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-leave-convo` |
| `chat-bsky-convo-list-convo-requests` | `chat.bsky.convo.listConvoRequests` | `query` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-convo-list-convo-requests` |
| `chat-bsky-convo-list-convos` | `chat.bsky.convo.listConvos` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-list-convos` |
| `chat-bsky-convo-lock-convo` | `chat.bsky.convo.lockConvo` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-convo-lock-convo` |
| `chat-bsky-convo-mute-convo` | `chat.bsky.convo.muteConvo` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-mute-convo` |
| `chat-bsky-convo-remove-reaction` | `chat.bsky.convo.removeReaction` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-remove-reaction` |
| `chat-bsky-convo-send-message` | `chat.bsky.convo.sendMessage` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-send-message` |
| `chat-bsky-convo-send-message-batch` | `chat.bsky.convo.sendMessageBatch` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-send-message-batch` |
| `chat-bsky-convo-unlock-convo` | `chat.bsky.convo.unlockConvo` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-convo-unlock-convo` |
| `chat-bsky-convo-unmute-convo` | `chat.bsky.convo.unmuteConvo` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-unmute-convo` |
| `chat-bsky-convo-update-all-read` | `chat.bsky.convo.updateAllRead` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-update-all-read` |
| `chat-bsky-convo-update-read` | `chat.bsky.convo.updateRead` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-convo-update-read` |
| `chat-bsky-group-add-members` | `chat.bsky.group.addMembers` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-add-members` |
| `chat-bsky-group-approve-join-request` | `chat.bsky.group.approveJoinRequest` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-approve-join-request` |
| `chat-bsky-group-create-group` | `chat.bsky.group.createGroup` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-create-group` |
| `chat-bsky-group-create-join-link` | `chat.bsky.group.createJoinLink` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-create-join-link` |
| `chat-bsky-group-disable-join-link` | `chat.bsky.group.disableJoinLink` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-disable-join-link` |
| `chat-bsky-group-edit-group` | `chat.bsky.group.editGroup` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-edit-group` |
| `chat-bsky-group-edit-join-link` | `chat.bsky.group.editJoinLink` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-edit-join-link` |
| `chat-bsky-group-enable-join-link` | `chat.bsky.group.enableJoinLink` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-enable-join-link` |
| `chat-bsky-group-get-join-link-previews` | `chat.bsky.group.getJoinLinkPreviews` | `query` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-get-join-link-previews` |
| `chat-bsky-group-list-join-requests` | `chat.bsky.group.listJoinRequests` | `query` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-list-join-requests` |
| `chat-bsky-group-list-mutual-groups` | `chat.bsky.group.listMutualGroups` | `query` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-list-mutual-groups` |
| `chat-bsky-group-reject-join-request` | `chat.bsky.group.rejectJoinRequest` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-reject-join-request` |
| `chat-bsky-group-remove-members` | `chat.bsky.group.removeMembers` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-remove-members` |
| `chat-bsky-group-request-join` | `chat.bsky.group.requestJoin` | `procedure` | `chat` | `lexicon-only` | `active-development` | `bluesky-safe-cli api chat-bsky-group-request-join` |
| `chat-bsky-moderation-get-actor-metadata` | `chat.bsky.moderation.getActorMetadata` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-moderation-get-actor-metadata` |
| `chat-bsky-moderation-get-message-context` | `chat.bsky.moderation.getMessageContext` | `query` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-moderation-get-message-context` |
| `chat-bsky-moderation-subscribe-mod-events` | `chat.bsky.moderation.subscribeModEvents` | `subscription` | `chat` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api chat-bsky-moderation-subscribe-mod-events` |
| `chat-bsky-moderation-update-actor-access` | `chat.bsky.moderation.updateActorAccess` | `procedure` | `chat` | `http-reference` | `stable` | `bluesky-safe-cli api chat-bsky-moderation-update-actor-access` |
| `com-atproto-admin-delete-account` | `com.atproto.admin.deleteAccount` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-delete-account` |
| `com-atproto-admin-disable-account-invites` | `com.atproto.admin.disableAccountInvites` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-disable-account-invites` |
| `com-atproto-admin-disable-invite-codes` | `com.atproto.admin.disableInviteCodes` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-disable-invite-codes` |
| `com-atproto-admin-enable-account-invites` | `com.atproto.admin.enableAccountInvites` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-enable-account-invites` |
| `com-atproto-admin-get-account-info` | `com.atproto.admin.getAccountInfo` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-get-account-info` |
| `com-atproto-admin-get-account-infos` | `com.atproto.admin.getAccountInfos` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-get-account-infos` |
| `com-atproto-admin-get-invite-codes` | `com.atproto.admin.getInviteCodes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-get-invite-codes` |
| `com-atproto-admin-get-subject-status` | `com.atproto.admin.getSubjectStatus` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-get-subject-status` |
| `com-atproto-admin-search-accounts` | `com.atproto.admin.searchAccounts` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-search-accounts` |
| `com-atproto-admin-send-email` | `com.atproto.admin.sendEmail` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-send-email` |
| `com-atproto-admin-update-account-email` | `com.atproto.admin.updateAccountEmail` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-update-account-email` |
| `com-atproto-admin-update-account-handle` | `com.atproto.admin.updateAccountHandle` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-update-account-handle` |
| `com-atproto-admin-update-account-password` | `com.atproto.admin.updateAccountPassword` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-update-account-password` |
| `com-atproto-admin-update-account-signing-key` | `com.atproto.admin.updateAccountSigningKey` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-update-account-signing-key` |
| `com-atproto-admin-update-subject-status` | `com.atproto.admin.updateSubjectStatus` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-admin-update-subject-status` |
| `com-atproto-identity-get-recommended-did-credentials` | `com.atproto.identity.getRecommendedDidCredentials` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-get-recommended-did-credentials` |
| `com-atproto-identity-refresh-identity` | `com.atproto.identity.refreshIdentity` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-refresh-identity` |
| `com-atproto-identity-request-plc-operation-signature` | `com.atproto.identity.requestPlcOperationSignature` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-request-plc-operation-signature` |
| `com-atproto-identity-resolve-did` | `com.atproto.identity.resolveDid` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-resolve-did` |
| `com-atproto-identity-resolve-handle` | `com.atproto.identity.resolveHandle` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-resolve-handle` |
| `com-atproto-identity-resolve-identity` | `com.atproto.identity.resolveIdentity` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-resolve-identity` |
| `com-atproto-identity-sign-plc-operation` | `com.atproto.identity.signPlcOperation` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-sign-plc-operation` |
| `com-atproto-identity-submit-plc-operation` | `com.atproto.identity.submitPlcOperation` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-submit-plc-operation` |
| `com-atproto-identity-update-handle` | `com.atproto.identity.updateHandle` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-identity-update-handle` |
| `com-atproto-label-query-labels` | `com.atproto.label.queryLabels` | `query` | `labeler` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-label-query-labels` |
| `com-atproto-label-subscribe-labels` | `com.atproto.label.subscribeLabels` | `subscription` | `labeler` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api com-atproto-label-subscribe-labels` |
| `com-atproto-lexicon-resolve-lexicon` | `com.atproto.lexicon.resolveLexicon` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-lexicon-resolve-lexicon` |
| `com-atproto-moderation-create-report` | `com.atproto.moderation.createReport` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-moderation-create-report` |
| `com-atproto-repo-apply-writes` | `com.atproto.repo.applyWrites` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-apply-writes` |
| `com-atproto-repo-create-record` | `com.atproto.repo.createRecord` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-create-record` |
| `com-atproto-repo-delete-record` | `com.atproto.repo.deleteRecord` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-delete-record` |
| `com-atproto-repo-describe-repo` | `com.atproto.repo.describeRepo` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-describe-repo` |
| `com-atproto-repo-get-record` | `com.atproto.repo.getRecord` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-get-record` |
| `com-atproto-repo-import-repo` | `com.atproto.repo.importRepo` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-import-repo` |
| `com-atproto-repo-list-missing-blobs` | `com.atproto.repo.listMissingBlobs` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-list-missing-blobs` |
| `com-atproto-repo-list-records` | `com.atproto.repo.listRecords` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-list-records` |
| `com-atproto-repo-put-record` | `com.atproto.repo.putRecord` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-put-record` |
| `com-atproto-repo-upload-blob` | `com.atproto.repo.uploadBlob` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-repo-upload-blob` |
| `com-atproto-server-activate-account` | `com.atproto.server.activateAccount` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-activate-account` |
| `com-atproto-server-check-account-status` | `com.atproto.server.checkAccountStatus` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-check-account-status` |
| `com-atproto-server-confirm-email` | `com.atproto.server.confirmEmail` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-confirm-email` |
| `com-atproto-server-create-account` | `com.atproto.server.createAccount` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-create-account` |
| `com-atproto-server-create-app-password` | `com.atproto.server.createAppPassword` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-create-app-password` |
| `com-atproto-server-create-invite-code` | `com.atproto.server.createInviteCode` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-create-invite-code` |
| `com-atproto-server-create-invite-codes` | `com.atproto.server.createInviteCodes` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-create-invite-codes` |
| `com-atproto-server-create-session` | `com.atproto.server.createSession` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-create-session` |
| `com-atproto-server-deactivate-account` | `com.atproto.server.deactivateAccount` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-deactivate-account` |
| `com-atproto-server-delete-account` | `com.atproto.server.deleteAccount` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-delete-account` |
| `com-atproto-server-delete-session` | `com.atproto.server.deleteSession` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-delete-session` |
| `com-atproto-server-describe-server` | `com.atproto.server.describeServer` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-describe-server` |
| `com-atproto-server-get-account-invite-codes` | `com.atproto.server.getAccountInviteCodes` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-get-account-invite-codes` |
| `com-atproto-server-get-service-auth` | `com.atproto.server.getServiceAuth` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-get-service-auth` |
| `com-atproto-server-get-session` | `com.atproto.server.getSession` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-get-session` |
| `com-atproto-server-list-app-passwords` | `com.atproto.server.listAppPasswords` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-list-app-passwords` |
| `com-atproto-server-refresh-session` | `com.atproto.server.refreshSession` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-refresh-session` |
| `com-atproto-server-request-account-delete` | `com.atproto.server.requestAccountDelete` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-request-account-delete` |
| `com-atproto-server-request-email-confirmation` | `com.atproto.server.requestEmailConfirmation` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-request-email-confirmation` |
| `com-atproto-server-request-email-update` | `com.atproto.server.requestEmailUpdate` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-request-email-update` |
| `com-atproto-server-request-password-reset` | `com.atproto.server.requestPasswordReset` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-request-password-reset` |
| `com-atproto-server-reserve-signing-key` | `com.atproto.server.reserveSigningKey` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-reserve-signing-key` |
| `com-atproto-server-reset-password` | `com.atproto.server.resetPassword` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-reset-password` |
| `com-atproto-server-revoke-app-password` | `com.atproto.server.revokeAppPassword` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-revoke-app-password` |
| `com-atproto-server-update-email` | `com.atproto.server.updateEmail` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-server-update-email` |
| `com-atproto-sync-get-blob` | `com.atproto.sync.getBlob` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-blob` |
| `com-atproto-sync-get-blocks` | `com.atproto.sync.getBlocks` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-blocks` |
| `com-atproto-sync-get-checkout` | `com.atproto.sync.getCheckout` | `query` | `entryway-or-pds` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api com-atproto-sync-get-checkout` |
| `com-atproto-sync-get-head` | `com.atproto.sync.getHead` | `query` | `entryway-or-pds` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api com-atproto-sync-get-head` |
| `com-atproto-sync-get-host-status` | `com.atproto.sync.getHostStatus` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-host-status` |
| `com-atproto-sync-get-latest-commit` | `com.atproto.sync.getLatestCommit` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-latest-commit` |
| `com-atproto-sync-get-record` | `com.atproto.sync.getRecord` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-record` |
| `com-atproto-sync-get-repo` | `com.atproto.sync.getRepo` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-repo` |
| `com-atproto-sync-get-repo-status` | `com.atproto.sync.getRepoStatus` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-get-repo-status` |
| `com-atproto-sync-list-blobs` | `com.atproto.sync.listBlobs` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-list-blobs` |
| `com-atproto-sync-list-hosts` | `com.atproto.sync.listHosts` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-list-hosts` |
| `com-atproto-sync-list-repos` | `com.atproto.sync.listRepos` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-list-repos` |
| `com-atproto-sync-list-repos-by-collection` | `com.atproto.sync.listReposByCollection` | `query` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-list-repos-by-collection` |
| `com-atproto-sync-notify-of-update` | `com.atproto.sync.notifyOfUpdate` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-notify-of-update` |
| `com-atproto-sync-request-crawl` | `com.atproto.sync.requestCrawl` | `procedure` | `entryway-or-pds` | `http-reference` | `stable` | `bluesky-safe-cli api com-atproto-sync-request-crawl` |
| `com-atproto-sync-subscribe-repos` | `com.atproto.sync.subscribeRepos` | `subscription` | `relay` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api com-atproto-sync-subscribe-repos` |
| `com-atproto-temp-add-reserved-handle` | `com.atproto.temp.addReservedHandle` | `procedure` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-add-reserved-handle` |
| `com-atproto-temp-check-handle-availability` | `com.atproto.temp.checkHandleAvailability` | `query` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-check-handle-availability` |
| `com-atproto-temp-check-signup-queue` | `com.atproto.temp.checkSignupQueue` | `query` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-check-signup-queue` |
| `com-atproto-temp-dereference-scope` | `com.atproto.temp.dereferenceScope` | `query` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-dereference-scope` |
| `com-atproto-temp-fetch-labels` | `com.atproto.temp.fetchLabels` | `query` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-fetch-labels` |
| `com-atproto-temp-request-phone-verification` | `com.atproto.temp.requestPhoneVerification` | `procedure` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-request-phone-verification` |
| `com-atproto-temp-revoke-account-credentials` | `com.atproto.temp.revokeAccountCredentials` | `procedure` | `entryway-or-pds` | `lexicon-only` | `temp` | `bluesky-safe-cli api com-atproto-temp-revoke-account-credentials` |
| `tools-ozone-communication-create-template` | `tools.ozone.communication.createTemplate` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-communication-create-template` |
| `tools-ozone-communication-delete-template` | `tools.ozone.communication.deleteTemplate` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-communication-delete-template` |
| `tools-ozone-communication-list-templates` | `tools.ozone.communication.listTemplates` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-communication-list-templates` |
| `tools-ozone-communication-update-template` | `tools.ozone.communication.updateTemplate` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-communication-update-template` |
| `tools-ozone-hosting-get-account-history` | `tools.ozone.hosting.getAccountHistory` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-hosting-get-account-history` |
| `tools-ozone-moderation-cancel-scheduled-actions` | `tools.ozone.moderation.cancelScheduledActions` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-cancel-scheduled-actions` |
| `tools-ozone-moderation-emit-event` | `tools.ozone.moderation.emitEvent` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-emit-event` |
| `tools-ozone-moderation-get-account-timeline` | `tools.ozone.moderation.getAccountTimeline` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-account-timeline` |
| `tools-ozone-moderation-get-event` | `tools.ozone.moderation.getEvent` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-event` |
| `tools-ozone-moderation-get-record` | `tools.ozone.moderation.getRecord` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-record` |
| `tools-ozone-moderation-get-records` | `tools.ozone.moderation.getRecords` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-records` |
| `tools-ozone-moderation-get-repo` | `tools.ozone.moderation.getRepo` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-repo` |
| `tools-ozone-moderation-get-reporter-stats` | `tools.ozone.moderation.getReporterStats` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-reporter-stats` |
| `tools-ozone-moderation-get-repos` | `tools.ozone.moderation.getRepos` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-repos` |
| `tools-ozone-moderation-get-subjects` | `tools.ozone.moderation.getSubjects` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-get-subjects` |
| `tools-ozone-moderation-list-scheduled-actions` | `tools.ozone.moderation.listScheduledActions` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-list-scheduled-actions` |
| `tools-ozone-moderation-query-events` | `tools.ozone.moderation.queryEvents` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-query-events` |
| `tools-ozone-moderation-query-statuses` | `tools.ozone.moderation.queryStatuses` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-query-statuses` |
| `tools-ozone-moderation-schedule-action` | `tools.ozone.moderation.scheduleAction` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-schedule-action` |
| `tools-ozone-moderation-search-repos` | `tools.ozone.moderation.searchRepos` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-moderation-search-repos` |
| `tools-ozone-queue-assign-moderator` | `tools.ozone.queue.assignModerator` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-assign-moderator` |
| `tools-ozone-queue-create-queue` | `tools.ozone.queue.createQueue` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-create-queue` |
| `tools-ozone-queue-delete-queue` | `tools.ozone.queue.deleteQueue` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-delete-queue` |
| `tools-ozone-queue-get-assignments` | `tools.ozone.queue.getAssignments` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-get-assignments` |
| `tools-ozone-queue-list-queues` | `tools.ozone.queue.listQueues` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-list-queues` |
| `tools-ozone-queue-route-reports` | `tools.ozone.queue.routeReports` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-route-reports` |
| `tools-ozone-queue-unassign-moderator` | `tools.ozone.queue.unassignModerator` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-unassign-moderator` |
| `tools-ozone-queue-update-queue` | `tools.ozone.queue.updateQueue` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-queue-update-queue` |
| `tools-ozone-report-assign-moderator` | `tools.ozone.report.assignModerator` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-assign-moderator` |
| `tools-ozone-report-create-activity` | `tools.ozone.report.createActivity` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-create-activity` |
| `tools-ozone-report-get-assignments` | `tools.ozone.report.getAssignments` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-get-assignments` |
| `tools-ozone-report-get-historical-stats` | `tools.ozone.report.getHistoricalStats` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-get-historical-stats` |
| `tools-ozone-report-get-latest-report` | `tools.ozone.report.getLatestReport` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-get-latest-report` |
| `tools-ozone-report-get-live-stats` | `tools.ozone.report.getLiveStats` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-get-live-stats` |
| `tools-ozone-report-get-report` | `tools.ozone.report.getReport` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-get-report` |
| `tools-ozone-report-list-activities` | `tools.ozone.report.listActivities` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-list-activities` |
| `tools-ozone-report-query-reports` | `tools.ozone.report.queryReports` | `query` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-query-reports` |
| `tools-ozone-report-reassign-queue` | `tools.ozone.report.reassignQueue` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-reassign-queue` |
| `tools-ozone-report-refresh-stats` | `tools.ozone.report.refreshStats` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-refresh-stats` |
| `tools-ozone-report-unassign-moderator` | `tools.ozone.report.unassignModerator` | `procedure` | `ozone` | `lexicon-only` | `lexicon-only` | `bluesky-safe-cli api tools-ozone-report-unassign-moderator` |
| `tools-ozone-safelink-add-rule` | `tools.ozone.safelink.addRule` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-safelink-add-rule` |
| `tools-ozone-safelink-query-events` | `tools.ozone.safelink.queryEvents` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-safelink-query-events` |
| `tools-ozone-safelink-query-rules` | `tools.ozone.safelink.queryRules` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-safelink-query-rules` |
| `tools-ozone-safelink-remove-rule` | `tools.ozone.safelink.removeRule` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-safelink-remove-rule` |
| `tools-ozone-safelink-update-rule` | `tools.ozone.safelink.updateRule` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-safelink-update-rule` |
| `tools-ozone-server-get-config` | `tools.ozone.server.getConfig` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-server-get-config` |
| `tools-ozone-set-add-values` | `tools.ozone.set.addValues` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-set-add-values` |
| `tools-ozone-set-delete-set` | `tools.ozone.set.deleteSet` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-set-delete-set` |
| `tools-ozone-set-delete-values` | `tools.ozone.set.deleteValues` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-set-delete-values` |
| `tools-ozone-set-get-values` | `tools.ozone.set.getValues` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-set-get-values` |
| `tools-ozone-set-query-sets` | `tools.ozone.set.querySets` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-set-query-sets` |
| `tools-ozone-set-upsert-set` | `tools.ozone.set.upsertSet` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-set-upsert-set` |
| `tools-ozone-setting-list-options` | `tools.ozone.setting.listOptions` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-setting-list-options` |
| `tools-ozone-setting-remove-options` | `tools.ozone.setting.removeOptions` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-setting-remove-options` |
| `tools-ozone-setting-upsert-option` | `tools.ozone.setting.upsertOption` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-setting-upsert-option` |
| `tools-ozone-signature-find-correlation` | `tools.ozone.signature.findCorrelation` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-signature-find-correlation` |
| `tools-ozone-signature-find-related-accounts` | `tools.ozone.signature.findRelatedAccounts` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-signature-find-related-accounts` |
| `tools-ozone-signature-search-accounts` | `tools.ozone.signature.searchAccounts` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-signature-search-accounts` |
| `tools-ozone-team-add-member` | `tools.ozone.team.addMember` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-team-add-member` |
| `tools-ozone-team-delete-member` | `tools.ozone.team.deleteMember` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-team-delete-member` |
| `tools-ozone-team-list-members` | `tools.ozone.team.listMembers` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-team-list-members` |
| `tools-ozone-team-update-member` | `tools.ozone.team.updateMember` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-team-update-member` |
| `tools-ozone-verification-grant-verifications` | `tools.ozone.verification.grantVerifications` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-verification-grant-verifications` |
| `tools-ozone-verification-list-verifications` | `tools.ozone.verification.listVerifications` | `query` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-verification-list-verifications` |
| `tools-ozone-verification-revoke-verifications` | `tools.ozone.verification.revokeVerifications` | `procedure` | `ozone` | `http-reference` | `stable` | `bluesky-safe-cli api tools-ozone-verification-revoke-verifications` |
