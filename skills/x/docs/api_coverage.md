# API coverage

Last audited (UTC): 2026-03-01

Last refreshed (UTC): `2026-03-01T11:10:43Z`

This file is generated from the pinned OpenAPI snapshot.

| operationId | method | path | tags | security | primary_cli |
|---|---|---|---|---|---|
| activityStream | GET | /2/activity/stream | Activity,Stream | BearerToken{} | `x-api-tool api activityStream` |
| addListsMember | POST | /2/lists/{id}/members | Lists | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api addListsMember` |
| addUserPublicKey | POST | /2/users/{id}/public_keys | Chat | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api addUserPublicKey` |
| appendMediaUpload | POST | /2/media/upload/{id}/append | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api appendMediaUpload` |
| blockUsersDms | POST | /2/users/{id}/dm/block | Users | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api blockUsersDms` |
| chatMediaDownload | GET | /2/chat/media/{conversation_id}/{media_hash_key} | Chat | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api chatMediaDownload` |
| chatMediaUploadAppend | POST | /2/chat/media/upload/{id}/append | Chat | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api chatMediaUploadAppend` |
| chatMediaUploadFinalize | POST | /2/chat/media/upload/{id}/finalize | Chat | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api chatMediaUploadFinalize` |
| chatMediaUploadInitialize | POST | /2/chat/media/upload/initialize | Chat | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api chatMediaUploadInitialize` |
| createAccountActivityReplayJob | POST | /2/account_activity/replay/webhooks/{webhook_id}/subscriptions/all | Account Activity | BearerToken{} | `x-api-tool api createAccountActivityReplayJob` |
| createAccountActivitySubscription | POST | /2/account_activity/webhooks/{webhook_id}/subscriptions/all | Account Activity | OAuth2UserToken{dm.read,dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api createAccountActivitySubscription` |
| createActivitySubscription | POST | /2/activity/subscriptions | Activity,Stream | BearerToken{}||OAuth2UserToken{dm.read,tweet.read}||UserToken{} | `x-api-tool api createActivitySubscription` |
| createCommunityNotes | POST | /2/notes | Community Notes | OAuth2UserToken{tweet.write}||UserToken{} | `x-api-tool api createCommunityNotes` |
| createComplianceJobs | POST | /2/compliance/jobs | Compliance | BearerToken{} | `x-api-tool api createComplianceJobs` |
| createDirectMessagesByConversationId | POST | /2/dm_conversations/{dm_conversation_id}/messages | Direct Messages | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api createDirectMessagesByConversationId` |
| createDirectMessagesByParticipantId | POST | /2/dm_conversations/with/{participant_id}/messages | Direct Messages | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api createDirectMessagesByParticipantId` |
| createDirectMessagesConversation | POST | /2/dm_conversations | Direct Messages | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api createDirectMessagesConversation` |
| createLists | POST | /2/lists | Lists | OAuth2UserToken{list.read,list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api createLists` |
| createMediaMetadata | POST | /2/media/metadata | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api createMediaMetadata` |
| createMediaSubtitles | POST | /2/media/subtitles | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api createMediaSubtitles` |
| createPosts | POST | /2/tweets | Tweets | OAuth2UserToken{tweet.read,tweet.write,users.read}||UserToken{} | `x-api-tool api createPosts` |
| createUsersBookmark | POST | /2/users/{id}/bookmarks | Bookmarks,Users | OAuth2UserToken{bookmark.write,tweet.read,users.read} | `x-api-tool api createUsersBookmark` |
| createWebhookReplayJob | POST | /2/webhooks/replay | Webhooks | BearerToken{} | `x-api-tool api createWebhookReplayJob` |
| createWebhooks | POST | /2/webhooks | Webhooks | BearerToken{}||UserToken{} | `x-api-tool api createWebhooks` |
| createWebhooksStreamLink | POST | /2/tweets/search/webhooks/{webhook_id} | Stream,Webhooks | BearerToken{} | `x-api-tool api createWebhooksStreamLink` |
| deleteAccountActivitySubscription | DELETE | /2/account_activity/webhooks/{webhook_id}/subscriptions/{user_id}/all | Account Activity | BearerToken{} | `x-api-tool api deleteAccountActivitySubscription` |
| deleteActivitySubscription | DELETE | /2/activity/subscriptions/{subscription_id} | Activity | BearerToken{} | `x-api-tool api deleteActivitySubscription` |
| deleteAllConnections | DELETE | /2/connections/all | Connections | BearerToken{} | `x-api-tool api deleteAllConnections` |
| deleteCommunityNotes | DELETE | /2/notes/{id} | Community Notes | OAuth2UserToken{tweet.write}||UserToken{} | `x-api-tool api deleteCommunityNotes` |
| deleteConnectionsByEndpoint | DELETE | /2/connections/{endpoint_id} | Connections | BearerToken{} | `x-api-tool api deleteConnectionsByEndpoint` |
| deleteConnectionsByUuids | DELETE | /2/connections | Connections | BearerToken{} | `x-api-tool api deleteConnectionsByUuids` |
| deleteDirectMessagesEvents | DELETE | /2/dm_events/{event_id} | Direct Messages | OAuth2UserToken{dm.read,dm.write}||UserToken{} | `x-api-tool api deleteDirectMessagesEvents` |
| deleteLists | DELETE | /2/lists/{id} | Lists | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api deleteLists` |
| deleteMediaSubtitles | DELETE | /2/media/subtitles | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api deleteMediaSubtitles` |
| deletePosts | DELETE | /2/tweets/{id} | Tweets | OAuth2UserToken{tweet.read,tweet.write,users.read}||UserToken{} | `x-api-tool api deletePosts` |
| deleteUsersBookmark | DELETE | /2/users/{id}/bookmarks/{tweet_id} | Bookmarks,Users | OAuth2UserToken{bookmark.write,tweet.read,users.read} | `x-api-tool api deleteUsersBookmark` |
| deleteWebhooks | DELETE | /2/webhooks/{webhook_id} | Webhooks | BearerToken{}||UserToken{} | `x-api-tool api deleteWebhooks` |
| deleteWebhooksStreamLink | DELETE | /2/tweets/search/webhooks/{webhook_id} | Stream,Webhooks | BearerToken{} | `x-api-tool api deleteWebhooksStreamLink` |
| evaluateCommunityNotes | POST | /2/evaluate_note | Community Notes | OAuth2UserToken{tweet.write}||UserToken{} | `x-api-tool api evaluateCommunityNotes` |
| finalizeMediaUpload | POST | /2/media/upload/{id}/finalize | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api finalizeMediaUpload` |
| followList | POST | /2/users/{id}/followed_lists | Lists,Users | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api followList` |
| followUser | POST | /2/users/{id}/following | Users | OAuth2UserToken{follows.write,tweet.read,users.read}||UserToken{} | `x-api-tool api followUser` |
| getAccountActivitySubscriptionCount | GET | /2/account_activity/subscriptions/count | Account Activity | BearerToken{} | `x-api-tool api getAccountActivitySubscriptionCount` |
| getAccountActivitySubscriptions | GET | /2/account_activity/webhooks/{webhook_id}/subscriptions/all/list | Account Activity | BearerToken{} | `x-api-tool api getAccountActivitySubscriptions` |
| getActivitySubscriptions | GET | /2/activity/subscriptions | Activity | BearerToken{} | `x-api-tool api getActivitySubscriptions` |
| getChatConversation | GET | /2/chat/conversations/{conversation_id} | Chat | OAuth2UserToken{dm.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getChatConversation` |
| getChatConversations | GET | /2/chat/conversations | Chat | OAuth2UserToken{dm.read,users.read}||UserToken{} | `x-api-tool api getChatConversations` |
| getCommunitiesById | GET | /2/communities/{id} | Communities | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getCommunitiesById` |
| getComplianceJobs | GET | /2/compliance/jobs | Compliance | BearerToken{} | `x-api-tool api getComplianceJobs` |
| getComplianceJobsById | GET | /2/compliance/jobs/{id} | Compliance | BearerToken{} | `x-api-tool api getComplianceJobsById` |
| getConnectionHistory | GET | /2/connections | Connections | BearerToken{} | `x-api-tool api getConnectionHistory` |
| getDirectMessagesEvents | GET | /2/dm_events | Direct Messages | OAuth2UserToken{dm.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getDirectMessagesEvents` |
| getDirectMessagesEventsByConversationId | GET | /2/dm_conversations/{id}/dm_events | Direct Messages | OAuth2UserToken{dm.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getDirectMessagesEventsByConversationId` |
| getDirectMessagesEventsById | GET | /2/dm_events/{event_id} | Direct Messages | OAuth2UserToken{dm.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getDirectMessagesEventsById` |
| getDirectMessagesEventsByParticipantId | GET | /2/dm_conversations/with/{participant_id}/dm_events | Direct Messages | OAuth2UserToken{dm.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getDirectMessagesEventsByParticipantId` |
| getInsights28Hr | GET | /2/insights/28hr | Tweets | OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api getInsights28Hr` |
| getInsightsHistorical | GET | /2/insights/historical | Tweets | OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api getInsightsHistorical` |
| getListsById | GET | /2/lists/{id} | Lists | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getListsById` |
| getListsFollowers | GET | /2/lists/{id}/followers | Lists,Users | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getListsFollowers` |
| getListsMembers | GET | /2/lists/{id}/members | Lists,Users | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getListsMembers` |
| getListsPosts | GET | /2/lists/{id}/tweets | Lists,Tweets | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getListsPosts` |
| getMediaAnalytics | GET | /2/media/analytics | Media | OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api getMediaAnalytics` |
| getMediaByMediaKey | GET | /2/media/{media_key} | Media | BearerToken{}||OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api getMediaByMediaKey` |
| getMediaByMediaKeys | GET | /2/media | Media | BearerToken{}||OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api getMediaByMediaKeys` |
| getMediaUploadStatus | GET | /2/media/upload | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api getMediaUploadStatus` |
| getNews | GET | /2/news/{id} | News | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getNews` |
| getOpenApiSpec | GET | /2/openapi.json | General | none | `x-api-tool api getOpenApiSpec` |
| getPostsAnalytics | GET | /2/tweets/analytics | Tweets | OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsAnalytics` |
| getPostsById | GET | /2/tweets/{id} | Tweets | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsById` |
| getPostsByIds | GET | /2/tweets | Tweets | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsByIds` |
| getPostsCountsAll | GET | /2/tweets/counts/all | Tweets | BearerToken{} | `x-api-tool api getPostsCountsAll` |
| getPostsCountsRecent | GET | /2/tweets/counts/recent | Tweets | BearerToken{} | `x-api-tool api getPostsCountsRecent` |
| getPostsLikingUsers | GET | /2/tweets/{id}/liking_users | Tweets,Users | OAuth2UserToken{like.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsLikingUsers` |
| getPostsQuotedPosts | GET | /2/tweets/{id}/quote_tweets | Tweets | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsQuotedPosts` |
| getPostsRepostedBy | GET | /2/tweets/{id}/retweeted_by | Tweets,Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsRepostedBy` |
| getPostsReposts | GET | /2/tweets/{id}/retweets | Tweets | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getPostsReposts` |
| getRuleCounts | GET | /2/tweets/search/stream/rules/counts | Stream,Tweets | BearerToken{} | `x-api-tool api getRuleCounts` |
| getRules | GET | /2/tweets/search/stream/rules | Stream,Tweets | BearerToken{} | `x-api-tool api getRules` |
| getSpacesBuyers | GET | /2/spaces/{id}/buyers | Spaces,Tweets | OAuth2UserToken{space.read,tweet.read,users.read} | `x-api-tool api getSpacesBuyers` |
| getSpacesByCreatorIds | GET | /2/spaces/by/creator_ids | Spaces | BearerToken{}||OAuth2UserToken{space.read,tweet.read,users.read} | `x-api-tool api getSpacesByCreatorIds` |
| getSpacesById | GET | /2/spaces/{id} | Spaces | BearerToken{}||OAuth2UserToken{space.read,tweet.read,users.read} | `x-api-tool api getSpacesById` |
| getSpacesByIds | GET | /2/spaces | Spaces | BearerToken{}||OAuth2UserToken{space.read,tweet.read,users.read} | `x-api-tool api getSpacesByIds` |
| getSpacesPosts | GET | /2/spaces/{id}/tweets | Spaces,Tweets | BearerToken{}||OAuth2UserToken{space.read,tweet.read,users.read} | `x-api-tool api getSpacesPosts` |
| getTrendsByWoeid | GET | /2/trends/by/woeid/{woeid} | Trends | BearerToken{} | `x-api-tool api getTrendsByWoeid` |
| getTrendsPersonalizedTrends | GET | /2/users/personalized_trends | Trends | OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getTrendsPersonalizedTrends` |
| getUsage | GET | /2/usage/tweets | Usage | BearerToken{} | `x-api-tool api getUsage` |
| getUserPublicKeys | GET | /2/users/{id}/public_keys | Chat | OAuth2UserToken{dm.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUserPublicKeys` |
| getUsersAffiliates | GET | /2/users/{id}/affiliates | Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersAffiliates` |
| getUsersBlocking | GET | /2/users/{id}/blocking | Users | OAuth2UserToken{block.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersBlocking` |
| getUsersBookmarkFolders | GET | /2/users/{id}/bookmarks/folders | Bookmarks,Users | OAuth2UserToken{bookmark.read,users.read} | `x-api-tool api getUsersBookmarkFolders` |
| getUsersBookmarks | GET | /2/users/{id}/bookmarks | Bookmarks,Users | OAuth2UserToken{bookmark.read,tweet.read,users.read} | `x-api-tool api getUsersBookmarks` |
| getUsersBookmarksByFolderId | GET | /2/users/{id}/bookmarks/folders/{folder_id} | Bookmarks,Users | OAuth2UserToken{bookmark.read,tweet.read,users.read} | `x-api-tool api getUsersBookmarksByFolderId` |
| getUsersById | GET | /2/users/{id} | Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersById` |
| getUsersByIds | GET | /2/users | Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersByIds` |
| getUsersByUsername | GET | /2/users/by/username/{username} | Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersByUsername` |
| getUsersByUsernames | GET | /2/users/by | Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersByUsernames` |
| getUsersFollowedLists | GET | /2/users/{id}/followed_lists | Lists,Users | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersFollowedLists` |
| getUsersFollowers | GET | /2/users/{id}/followers | Users | BearerToken{}||OAuth2UserToken{follows.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersFollowers` |
| getUsersFollowing | GET | /2/users/{id}/following | Users | BearerToken{}||OAuth2UserToken{follows.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersFollowing` |
| getUsersLikedPosts | GET | /2/users/{id}/liked_tweets | Tweets,Users | OAuth2UserToken{like.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersLikedPosts` |
| getUsersListMemberships | GET | /2/users/{id}/list_memberships | Lists,Users | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersListMemberships` |
| getUsersMe | GET | /2/users/me | Users | OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersMe` |
| getUsersMentions | GET | /2/users/{id}/mentions | Tweets,Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersMentions` |
| getUsersMuting | GET | /2/users/{id}/muting | Users | OAuth2UserToken{mute.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersMuting` |
| getUsersOwnedLists | GET | /2/users/{id}/owned_lists | Lists,Users | BearerToken{}||OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersOwnedLists` |
| getUsersPinnedLists | GET | /2/users/{id}/pinned_lists | Lists,Users | OAuth2UserToken{list.read,tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersPinnedLists` |
| getUsersPosts | GET | /2/users/{id}/tweets | Tweets,Users | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersPosts` |
| getUsersRepostsOfMe | GET | /2/users/reposts_of_me | Users | OAuth2UserToken{timeline.read,tweet.read}||UserToken{} | `x-api-tool api getUsersRepostsOfMe` |
| getUsersTimeline | GET | /2/users/{id}/timelines/reverse_chronological | Tweets,Users | OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api getUsersTimeline` |
| getWebhooks | GET | /2/webhooks | Webhooks | BearerToken{} | `x-api-tool api getWebhooks` |
| getWebhooksStreamLinks | GET | /2/tweets/search/webhooks | Stream,Webhooks | BearerToken{} | `x-api-tool api getWebhooksStreamLinks` |
| hidePostsReply | PUT | /2/tweets/{tweet_id}/hidden | Tweets | OAuth2UserToken{tweet.moderate.write,tweet.read,users.read}||UserToken{} | `x-api-tool api hidePostsReply` |
| initializeMediaUpload | POST | /2/media/upload/initialize | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api initializeMediaUpload` |
| likePost | POST | /2/users/{id}/likes | Tweets,Users | OAuth2UserToken{like.write,tweet.read,users.read}||UserToken{} | `x-api-tool api likePost` |
| markChatConversationRead | POST | /2/chat/conversations/{conversation_id}/read | Chat | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api markChatConversationRead` |
| mediaUpload | POST | /2/media/upload | Media | OAuth2UserToken{media.write}||UserToken{} | `x-api-tool api mediaUpload` |
| muteUser | POST | /2/users/{id}/muting | Users | OAuth2UserToken{mute.write,tweet.read,users.read}||UserToken{} | `x-api-tool api muteUser` |
| pinList | POST | /2/users/{id}/pinned_lists | Lists,Users | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api pinList` |
| removeListsMemberByUserId | DELETE | /2/lists/{id}/members/{user_id} | Lists | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api removeListsMemberByUserId` |
| repostPost | POST | /2/users/{id}/retweets | Tweets,Users | OAuth2UserToken{tweet.read,tweet.write,users.read}||UserToken{} | `x-api-tool api repostPost` |
| searchCommunities | GET | /2/communities/search | Communities | OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api searchCommunities` |
| searchCommunityNotesWritten | GET | /2/notes/search/notes_written | Community Notes | OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api searchCommunityNotesWritten` |
| searchEligiblePosts | GET | /2/notes/search/posts_eligible_for_notes | Community Notes | OAuth2UserToken{tweet.read}||UserToken{} | `x-api-tool api searchEligiblePosts` |
| searchNews | GET | /2/news/search | News | BearerToken{}||OAuth2UserToken{tweet.read,users.read} | `x-api-tool api searchNews` |
| searchPostsAll | GET | /2/tweets/search/all | Tweets | BearerToken{} | `x-api-tool api searchPostsAll` |
| searchPostsRecent | GET | /2/tweets/search/recent | Tweets | BearerToken{}||OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api searchPostsRecent` |
| searchSpaces | GET | /2/spaces/search | Spaces | BearerToken{}||OAuth2UserToken{space.read,tweet.read,users.read} | `x-api-tool api searchSpaces` |
| searchUsers | GET | /2/users/search | Users | OAuth2UserToken{tweet.read,users.read}||UserToken{} | `x-api-tool api searchUsers` |
| sendChatMessage | POST | /2/chat/conversations/{conversation_id}/messages | Chat | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api sendChatMessage` |
| sendChatTypingIndicator | POST | /2/chat/conversations/{conversation_id}/typing | Chat | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api sendChatTypingIndicator` |
| streamLabelsCompliance | GET | /2/tweets/label/stream | Compliance,Stream | BearerToken{} | `x-api-tool api streamLabelsCompliance` |
| streamLikesCompliance | GET | /2/likes/compliance/stream | Compliance,Stream | BearerToken{} | `x-api-tool api streamLikesCompliance` |
| streamLikesFirehose | GET | /2/likes/firehose/stream | Likes,Stream | BearerToken{} | `x-api-tool api streamLikesFirehose` |
| streamLikesSample10 | GET | /2/likes/sample10/stream | Likes,Stream | BearerToken{} | `x-api-tool api streamLikesSample10` |
| streamPosts | GET | /2/tweets/search/stream | Stream,Tweets | BearerToken{} | `x-api-tool api streamPosts` |
| streamPostsCompliance | GET | /2/tweets/compliance/stream | Compliance,Stream | BearerToken{} | `x-api-tool api streamPostsCompliance` |
| streamPostsFirehose | GET | /2/tweets/firehose/stream | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsFirehose` |
| streamPostsFirehoseEn | GET | /2/tweets/firehose/stream/lang/en | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsFirehoseEn` |
| streamPostsFirehoseJa | GET | /2/tweets/firehose/stream/lang/ja | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsFirehoseJa` |
| streamPostsFirehoseKo | GET | /2/tweets/firehose/stream/lang/ko | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsFirehoseKo` |
| streamPostsFirehosePt | GET | /2/tweets/firehose/stream/lang/pt | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsFirehosePt` |
| streamPostsSample | GET | /2/tweets/sample/stream | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsSample` |
| streamPostsSample10 | GET | /2/tweets/sample10/stream | Stream,Tweets | BearerToken{} | `x-api-tool api streamPostsSample10` |
| streamUsersCompliance | GET | /2/users/compliance/stream | Compliance,Stream | BearerToken{} | `x-api-tool api streamUsersCompliance` |
| unblockUsersDms | POST | /2/users/{id}/dm/unblock | Users | OAuth2UserToken{dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api unblockUsersDms` |
| unfollowList | DELETE | /2/users/{id}/followed_lists/{list_id} | Lists,Users | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api unfollowList` |
| unfollowUser | DELETE | /2/users/{source_user_id}/following/{target_user_id} | Users | OAuth2UserToken{follows.write,tweet.read,users.read}||UserToken{} | `x-api-tool api unfollowUser` |
| unlikePost | DELETE | /2/users/{id}/likes/{tweet_id} | Tweets,Users | OAuth2UserToken{like.write,tweet.read,users.read}||UserToken{} | `x-api-tool api unlikePost` |
| unmuteUser | DELETE | /2/users/{source_user_id}/muting/{target_user_id} | Users | OAuth2UserToken{mute.write,tweet.read,users.read}||UserToken{} | `x-api-tool api unmuteUser` |
| unpinList | DELETE | /2/users/{id}/pinned_lists/{list_id} | Lists,Users | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api unpinList` |
| unrepostPost | DELETE | /2/users/{id}/retweets/{source_tweet_id} | Tweets,Users | OAuth2UserToken{tweet.read,tweet.write,users.read}||UserToken{} | `x-api-tool api unrepostPost` |
| updateActivitySubscription | PUT | /2/activity/subscriptions/{subscription_id} | Activity | BearerToken{} | `x-api-tool api updateActivitySubscription` |
| updateLists | PUT | /2/lists/{id} | Lists | OAuth2UserToken{list.write,tweet.read,users.read}||UserToken{} | `x-api-tool api updateLists` |
| updateRules | POST | /2/tweets/search/stream/rules | Stream,Tweets | BearerToken{} | `x-api-tool api updateRules` |
| validateAccountActivitySubscription | GET | /2/account_activity/webhooks/{webhook_id}/subscriptions/all | Account Activity | OAuth2UserToken{dm.read,dm.write,tweet.read,users.read}||UserToken{} | `x-api-tool api validateAccountActivitySubscription` |
| validateWebhooks | PUT | /2/webhooks/{webhook_id} | Webhooks | BearerToken{}||UserToken{} | `x-api-tool api validateWebhooks` |
