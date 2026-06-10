# API coverage

Purpose:
- Make the LinkedIn Ads scope measurable.
- Show what this tool ships now, and what would still be docs-only if LinkedIn's docs were too incomplete for safe wiring.

Rules:
- Every unique documented operation in the chosen ad scope must be accounted for here.
- Shared helper resources such as `posts`, `creatives`, `events`, and `inMailContents` are included only where LinkedIn's ad docs directly depend on them.
- If the docs are incomplete, say that clearly instead of guessing.

## Summary

- Provider: LinkedIn Marketing Developer Platform
- API base URL: `https://api.linkedin.com/rest`
- Auth method: member-consent OAuth bearer token with ad-product scopes
- Default LinkedIn version target for this build: `202605`
- Last audited (UTC): 2026-05-24

## Gate labels used here

- `access-gated`: needs LinkedIn product approval or product-specific permissions
- `private-api-gated`: LinkedIn marks this product as private or restricted
- `tier-gated`: live create or edit behavior depends on account tier or role limits
- `live-unverified`: docs are mapped, but this repo has not yet proved the call live with approved access

## Coverage legend

- `implemented`: operation exists in the shipped CLI and has matching command runtime + docs
- `documented-only`: LinkedIn documents it, but the docs are too incomplete or the operation is intentionally not wired yet

## Write rollback contract

All write-capable LinkedIn operations in this tool currently end at `irreversible_and_clearly_labeled`.
The CLI can dry-run and save plans, but it does not capture before-state snapshots or provider backups.
That is why every live write apply now requires `--ack-irreversible`, even when LinkedIn exposes another write endpoint for the same resource family.
In the table below, `--apply` and `--apply --yes` show the base safety tier only. Add `--ack-irreversible` to every live write apply.

## Coverage ledger

| Family | Operation | Method + path | CLI shape | Safety | Gate tags | Status | Notes |
|---|---|---|---|---|---|---|---|
| account-intelligence | get-account-intelligence | `GET /accountIntelligence?q=account` | `account-intelligence get-account-intelligence` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private Company Intelligence endpoint. |
| ad-account-trust-preferences | get | `GET /adAccountTrustPreferences/{sponsored_account_id}` | `ad-account-trust-preferences get` | read | `access-gated, live-unverified` | implemented | Used by audience restriction workflows. |
| ad-account-trust-preferences | update | `PUT /adAccountTrustPreferences/{sponsored_account_id}` | `ad-account-trust-preferences update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Write path tied to trust settings. |
| ad-account-users | set-role | `PUT /adAccountUsers/(account:{account_urn},user:{person_urn})` | `ad-account-users set-role` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Create or replace a role binding. |
| ad-account-users | update-role | `POST /adAccountUsers/(account:{account_urn},user:{person_urn})` | `ad-account-users update-role` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Partial update for a role binding. |
| ad-account-users | get | `GET /adAccountUsers/(account:{account_urn},user:{person_urn})` | `ad-account-users get` | read | `access-gated, live-unverified` | implemented | Read one role binding. |
| ad-account-users | list-authenticated-user | `GET /adAccountUsers?q=authenticatedUser` | `ad-account-users list-authenticated-user` | read | `access-gated, live-unverified` | implemented | Helpful for auth checks. |
| ad-account-users | list-by-account | `GET /adAccountUsers?q=accounts` | `ad-account-users list-by-account` | read | `access-gated, live-unverified` | implemented | Lists members on one account. |
| ad-account-users | delete | `DELETE /adAccountUsers/(account:{account_urn},user:{person_urn})` | `ad-account-users delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Destructive role removal. |
| ad-accounts | create | `POST /adAccounts` | `ad-accounts create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Broad live create rights need Standard tier. |
| ad-accounts | get | `GET /adAccounts/{ad_account_id}` | `ad-accounts get` | read | `access-gated, live-unverified` | implemented | Read one ad account. |
| ad-accounts | update | `POST /adAccounts/{ad_account_id}` | `ad-accounts update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Edit rights depend on role and tier. |
| ad-accounts | delete | `DELETE /adAccounts/{ad_account_id}` | `ad-accounts delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Destructive account removal. |
| ad-accounts | search | `GET /adAccounts?q=search` | `ad-accounts search` | read | `access-gated, live-unverified` | implemented | Search with rest.li search filters. |
| ad-campaign-groups | create | `POST /adAccounts/{ad_account_id}/adCampaignGroups` | `ad-campaign-groups create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Create one campaign group. |
| ad-campaign-groups | get | `GET /adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}` | `ad-campaign-groups get` | read | `access-gated, live-unverified` | implemented | Read one campaign group. |
| ad-campaign-groups | search | `GET /adAccounts/{ad_account_id}/adCampaignGroups?q=search` | `ad-campaign-groups search` | read | `access-gated, live-unverified` | implemented | Search campaign groups. |
| ad-campaign-groups | batch-get | `GET /adAccounts/{ad_account_id}/adCampaignGroups?ids=List(...)` | `ad-campaign-groups batch-get` | read | `access-gated, live-unverified` | implemented | Batch get by ids. |
| ad-campaign-groups | update | `POST /adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}` | `ad-campaign-groups update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Update one campaign group. |
| ad-campaign-groups | batch-update | `POST /adAccounts/{ad_account_id}/adCampaignGroups?ids=List(...)` | `ad-campaign-groups batch-update` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch update by ids. |
| ad-campaign-groups | delete | `DELETE /adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}` | `ad-campaign-groups delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Destructive delete. |
| ad-campaign-groups | batch-delete | `DELETE /adAccounts/{ad_account_id}/adCampaignGroups?ids=List(...)` | `ad-campaign-groups batch-delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch delete. |
| ad-campaigns | create | `POST /adAccounts/{ad_account_id}/adCampaigns` | `ad-campaigns create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Base campaign create. |
| ad-campaigns | get | `GET /adAccounts/{ad_account_id}/adCampaigns/{campaign_id}` | `ad-campaigns get` | read | `access-gated, live-unverified` | implemented | Read one campaign. |
| ad-campaigns | search | `GET /adAccounts/{ad_account_id}/adCampaigns?q=search` | `ad-campaigns search` | read | `access-gated, live-unverified` | implemented | Search campaigns. |
| ad-campaigns | batch-get | `GET /adAccounts/{ad_account_id}/adCampaigns?ids=List(...)` | `ad-campaigns batch-get` | read | `access-gated, live-unverified` | implemented | Batch get campaigns. |
| ad-campaigns | update | `POST /adAccounts/{ad_account_id}/adCampaigns/{campaign_id}` | `ad-campaigns update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Shared by LAN and audience restriction docs too. |
| ad-campaigns | delete | `DELETE /adAccounts/{ad_account_id}/adCampaigns/{campaign_id}` | `ad-campaigns delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Destructive delete. |
| ad-analytics | analytics | `GET /adAnalytics?q=analytics` | `ad-analytics analytics` | read | `access-gated, live-unverified` | implemented | One-pivot analytics. |
| ad-analytics | statistics | `GET /adAnalytics?q=statistics` | `ad-analytics statistics` | read | `access-gated, live-unverified` | implemented | Multi-pivot stats query. |
| ad-analytics | attributed-revenue-metrics | `GET /adAnalytics?q=attributedRevenueMetrics` | `ad-analytics attributed-revenue-metrics` | read | `access-gated, live-unverified` | implemented | Revenue attribution metrics. |
| ad-budget-pricing | forecast-price | `GET /adBudgetPricing?q=criteriaV2` | `ad-budget-pricing forecast-price` | read | `access-gated, live-unverified` | implemented | Price guidance endpoint. |
| ad-page-sets | create | `POST /adPageSets` | `ad-page-sets create` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Used by website retargeting. |
| ad-previews | get-by-creative | `GET /adPreviews?q=creative` | `ad-previews get-by-creative` | read | `access-gated, live-unverified` | implemented | Preview metadata. |
| ad-previews | live-preview-for-creative | `POST /adPreviews?action=livePreviewForCreative` | `ad-previews live-preview-for-creative` | read | `access-gated, live-unverified` | implemented | Read-like action; no live state change. |
| ad-previews | live-preview-for-creative-inline | `POST /adPreviews?action=livePreviewForCreativeInline` | `ad-previews live-preview-for-creative-inline` | read | `access-gated, live-unverified` | implemented | Read-like inline preview action. |
| ad-publisher-restrictions | get | `GET /adPublisherRestrictions/{restriction_id}` | `ad-publisher-restrictions get` | read | `access-gated, live-unverified` | implemented | Read one restriction bundle. |
| ad-publisher-restrictions | list-by-entity | `GET /adPublisherRestrictions?q=entity` | `ad-publisher-restrictions list-by-entity` | read | `access-gated, live-unverified` | implemented | List restrictions by entity. |
| ad-publisher-restrictions | create | `POST /adPublisherRestrictions` | `ad-publisher-restrictions create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Create or replace restrictions. |
| ad-publisher-restrictions | generate-download-url | `POST /adPublisherRestrictions?action=generateRestrictionsDownloadUrl` | `ad-publisher-restrictions generate-download-url` | read | `access-gated, live-unverified` | implemented | Read-like action. |
| ad-publisher-restrictions | generate-upload-url | `POST /adPublisherRestrictions?action=generateRestrictionsUploadUrl` | `ad-publisher-restrictions generate-upload-url` | read | `access-gated, live-unverified` | implemented | Read-like action. |
| ad-segment-sources | associate | `PUT /adSegmentSources/source={ad_page_set_urn}&segment={ad_segment_urn}` | `ad-segment-sources associate` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Website retargeting link. |
| ad-segment-sources | delete-association | `DELETE /adSegmentSources/source={ad_page_set_urn}&segment={ad_segment_urn}` | `ad-segment-sources delete-association` | `--apply --yes` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Remove retargeting link. |
| ad-segments | get | `GET /adSegments/{segment_id}` | `ad-segments get` | read | `access-gated, private-api-gated, live-unverified` | implemented | Read one ad segment. |
| ad-segments | update | `POST /adSegments/{segment_id}` | `ad-segments update` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Update one ad segment. |
| ad-segments | list-by-account | `GET /adSegments?q=accounts` | `ad-segments list-by-account` | read | `access-gated, private-api-gated, live-unverified` | implemented | Documented in Matched Audiences overview. |
| ad-supply-forecasts | forecast | `GET /adSupplyForecasts?q=criteriaV2` | `ad-supply-forecasts forecast` | read | `access-gated, live-unverified` | implemented | Supply forecast read. |
| ad-target-templates | create | `POST /adTargetTemplates` | `ad-target-templates create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Saved audience template create. |
| ad-target-templates | get | `GET /adTargetTemplates/{template_id}` | `ad-target-templates get` | read | `access-gated, live-unverified` | implemented | Docs show a trailing slash sample; path is inferred. |
| ad-target-templates | update | `POST /adTargetTemplates/{template_id}` | `ad-target-templates update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Docs show a trailing slash sample; path is inferred. |
| ad-target-templates | delete | `DELETE /adTargetTemplates/{template_id}` | `ad-target-templates delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Inferred single-item path. |
| ad-target-templates | batch-delete | `DELETE /adTargetTemplates?ids=List(...)` | `ad-target-templates batch-delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch delete. |
| ad-target-templates | list-by-account | `GET /adTargetTemplates?q=account` | `ad-target-templates list-by-account` | read | `access-gated, live-unverified` | implemented | List templates by account. |
| ad-targeting-entities | list-by-facet | `GET /adTargetingEntities?q=adTargetingFacet` | `ad-targeting-entities list-by-facet` | read | `access-gated, live-unverified` | implemented | Base entity list. |
| ad-targeting-entities | similar-entities | `GET /adTargetingEntities?q=similarEntities` | `ad-targeting-entities similar-entities` | read | `access-gated, live-unverified` | implemented | Similar entity lookup. |
| ad-targeting-entities | typeahead | `GET /adTargetingEntities?q=typeahead` | `ad-targeting-entities typeahead` | read | `access-gated, live-unverified` | implemented | Typeahead entity lookup. |
| ad-targeting-entities | get-by-urns | `GET /adTargetingEntities?q=urns` | `ad-targeting-entities get-by-urns` | read | `access-gated, live-unverified` | implemented | Resolve known URNs. |
| ad-targeting-facets | list | `GET /adTargetingFacets` | `ad-targeting-facets list` | read | `access-gated, live-unverified` | implemented | List targeting facets. |
| ad-tracking-parameters | upsert-for-campaign | `PUT /adTrackingParameters/(adEntity:(sponsoredCampaign:{campaign_urn}))` | `ad-tracking-parameters upsert-for-campaign` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Dynamic UTM create or update. |
| ad-tracking-parameters | get-for-campaign | `GET /adTrackingParameters/(adEntity:(sponsoredCampaign:{campaign_urn}))` | `ad-tracking-parameters get-for-campaign` | read | `access-gated, live-unverified` | implemented | Dynamic UTM read. |
| ad-tracking-parameters | delete-for-campaign | `DELETE /adTrackingParameters/(adEntity:(sponsoredCampaign:{campaign_urn}))` | `ad-tracking-parameters delete-for-campaign` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Dynamic UTM delete. |
| audience-counts | estimate | `GET /audienceCounts?q=targetingCriteriaV2` | `audience-counts estimate` | read | `access-gated, live-unverified` | implemented | Read audience size estimate. |
| audience-insights | audience-insights | `POST /targetingAudienceInsights?action=audienceInsights` | `audience-insights audience-insights` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private API action. |
| campaign-conversions | associate | `PUT /campaignConversions/(campaign:{campaign_urn},conversion:{conversion_urn})` | `campaign-conversions associate` | `--apply` | `access-gated, live-unverified` | implemented | Single association write. |
| campaign-conversions | batch-associate | `PUT /campaignConversions?ids=List(...)` | `campaign-conversions batch-associate` | `--apply --yes` | `access-gated, live-unverified` | implemented | Batch association write. |
| campaign-conversions | get | `GET /campaignConversions/(campaign:{campaign_urn},conversion:{conversion_urn})` | `campaign-conversions get` | read | `access-gated, live-unverified` | implemented | Read one association. |
| campaign-conversions | batch-get | `GET /campaignConversions?ids=List(...)` | `campaign-conversions batch-get` | read | `access-gated, live-unverified` | implemented | Batch association read. |
| campaign-conversions | list-by-campaigns | `GET /campaignConversions?q=campaigns` | `campaign-conversions list-by-campaigns` | read | `access-gated, live-unverified` | implemented | List by campaign list. |
| campaign-conversions | delete | `DELETE /campaignConversions/(campaign:{campaign_urn},conversion:{conversion_urn})` | `campaign-conversions delete` | `--apply --yes` | `access-gated, live-unverified` | implemented | Remove one association. |
| campaign-conversions | batch-delete | `DELETE /campaignConversions?ids=List(...)` | `campaign-conversions batch-delete` | `--apply --yes` | `access-gated, live-unverified` | implemented | Batch remove associations. |
| conversation-ads | create | `POST /conversationAds` | `conversation-ads create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Create conversation ad shell. |
| conversation-ads | get | `GET /conversationAds/{conversation_urn}` | `conversation-ads get` | read | `access-gated, live-unverified` | implemented | Read one conversation ad. |
| conversation-ads | update | `POST /conversationAds/{conversation_urn}` | `conversation-ads update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Update one conversation ad. |
| conversation-ads | batch-get | `GET /conversationAds?ids=List(...)` | `conversation-ads batch-get` | read | `access-gated, live-unverified` | implemented | Batch read. |
| conversation-ads | create-sponsored-message-content | `POST /conversationAds/{conversation_urn}/sponsoredMessageContents` | `conversation-ads create-sponsored-message-content` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Nested message node create. |
| conversation-ads | get-sponsored-message-content | `GET /conversationAds/{conversation_urn}/sponsoredMessageContents/{message_urn}` | `conversation-ads get-sponsored-message-content` | read | `access-gated, live-unverified` | implemented | Nested message node read. |
| conversation-ads | list-sponsored-message-contents | `GET /conversationAds/{conversation_urn}/sponsoredMessageContents` | `conversation-ads list-sponsored-message-contents` | read | `access-gated, live-unverified` | implemented | Nested message node list. |
| conversation-ads | update-sponsored-message-content | `POST /conversationAds/{conversation_urn}/sponsoredMessageContents/{message_urn}` | `conversation-ads update-sponsored-message-content` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Nested message node update. |
| conversation-ads | batch-update-sponsored-message-contents | `POST /conversationAds/{conversation_urn}/sponsoredMessageContents?ids=List(...)` | `conversation-ads batch-update-sponsored-message-contents` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Nested batch update. |
| conversation-ads | batch-delete-sponsored-message-contents | `DELETE /conversationAds/{conversation_urn}/sponsoredMessageContents?ids=List(...)` | `conversation-ads batch-delete-sponsored-message-contents` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Nested batch delete. |
| conversion-events | create | `POST /conversionEvents` | `conversion-events create` | `--apply` | `access-gated, live-unverified` | implemented | Event ingestion call. |
| conversions | create | `POST /conversions` | `conversions create` | `--apply` | `access-gated, live-unverified` | implemented | Create one conversion definition. |
| conversions | get | `GET /conversions/{conversion_id}` | `conversions get` | read | `access-gated, live-unverified` | implemented | Read one conversion definition. |
| conversions | batch-get | `GET /conversions?ids=List(...)` | `conversions batch-get` | read | `access-gated, live-unverified` | implemented | Batch read conversions. |
| conversions | list-by-account | `GET /conversions?q=account` | `conversions list-by-account` | read | `access-gated, live-unverified` | implemented | List conversions for one account. |
| conversions | update | `POST /conversions/{conversion_id}` | `conversions update` | `--apply` | `access-gated, live-unverified` | implemented | Update one conversion definition. |
| conversions | batch-update | `POST /conversions?ids=List(...)` | `conversions batch-update` | `--apply --yes` | `access-gated, live-unverified` | implemented | Batch update conversions. |
| dmp-engagement-source-types | list | `GET /dmpEngagementSourceTypes` | `dmp-engagement-source-types list` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private list endpoint. |
| dmp-engagement-source-types | get | `GET /dmpEngagementSourceTypes/{source_type}` | `dmp-engagement-source-types get` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private source-type read. |
| dmp-engagement-source-types | list-triggers | `GET /dmpEngagementSourceTypes/{source_type}/dmpEngagementTriggers` | `dmp-engagement-source-types list-triggers` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private trigger list. |
| dmp-engagement-source-types | get-trigger | `GET /dmpEngagementSourceTypes/{source_type}/dmpEngagementTriggers/{trigger_id}` | `dmp-engagement-source-types get-trigger` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private trigger read. |
| dmp-segments | create | `POST /dmpSegments` | `dmp-segments create` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Base private segment create. |
| dmp-segments | get | `GET /dmpSegments/{segment_id}` | `dmp-segments get` | read | `access-gated, private-api-gated, live-unverified` | implemented | Base private segment read. |
| dmp-segments | batch-get | `GET /dmpSegments?ids=List(...)` | `dmp-segments batch-get` | read | `access-gated, private-api-gated, live-unverified` | implemented | Batch private segment read. |
| dmp-segments | list-by-account | `GET /dmpSegments?q=account` | `dmp-segments list-by-account` | read | `access-gated, private-api-gated, live-unverified` | implemented | List private segments by account. |
| dmp-segments | update | `POST /dmpSegments/{segment_id}` | `dmp-segments update` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Base private segment update. |
| dmp-segments | delete | `DELETE /dmpSegments/{segment_id}` | `dmp-segments delete` | `--apply --yes` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Base private segment delete. |
| dmp-segments | batch-delete | `DELETE /dmpSegments?ids=List(...)` | `dmp-segments batch-delete` | `--apply --yes` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Batch private segment delete. |
| dmp-segments | generate-upload-url | `POST /dmpSegments?action=generateUploadUrl` | `dmp-segments generate-upload-url` | read | `access-gated, private-api-gated, live-unverified` | implemented | Read-like upload-url action. |
| dmp-segments | upload-list-state | `POST /dmpSegments/{segment_id}` | `dmp-segments upload-list-state` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Docs sample path is truncated; path is inferred. |
| dmp-segments | create-engagement-rule | `POST /dmpSegments/{segment_id}/engagementRules` | `dmp-segments create-engagement-rule` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Engagement retargeting rule create. |
| dmp-segments | get-engagement-rule | `GET /dmpSegments/{segment_id}/engagementRules/{rule_id}` | `dmp-segments get-engagement-rule` | read | `access-gated, private-api-gated, live-unverified` | implemented | Engagement rule read. |
| dmp-segments | list-engagement-rules | `GET /dmpSegments/{segment_id}/engagementRules` | `dmp-segments list-engagement-rules` | read | `access-gated, private-api-gated, live-unverified` | implemented | Engagement rule list. |
| dmp-segments | delete-engagement-rule | `DELETE /dmpSegments/{segment_id}/engagementRules/{rule_id}` | `dmp-segments delete-engagement-rule` | `--apply --yes` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Engagement rule delete. |
| dmp-segments | batch-delete-engagement-rules | `DELETE /dmpSegments/{segment_id}/engagementRules?ids=List(...)` | `dmp-segments batch-delete-engagement-rules` | `--apply --yes` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Engagement rule batch delete. |
| dmp-segments | create-company-match | `POST /dmpSegments/{segment_id}/companies` | `dmp-segments create-company-match` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Company list upload. |
| dmp-segments | create-user-match | `POST /dmpSegments/{segment_id}/users` | `dmp-segments create-user-match` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | User list upload. |
| dmp-segments | create-destination | `POST /dmpSegments/{segment_id}/destinations` | `dmp-segments create-destination` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Destination create. |
| dmp-segments | get-destination | `GET /dmpSegments/{segment_id}/destinations/{destination_id}` | `dmp-segments get-destination` | read | `access-gated, private-api-gated, live-unverified` | implemented | Destination read. |
| dmp-segments | list-destinations | `GET /dmpSegments/{segment_id}/destinations` | `dmp-segments list-destinations` | read | `access-gated, private-api-gated, live-unverified` | implemented | Destination list. |
| dmp-segments | create-predictive-audience | `POST /dmpSegments/{segment_id}/businessObjectiveBasedAudiences` | `dmp-segments create-predictive-audience` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Predictive audience create. |
| dmp-segments | get-predictive-audience | `GET /dmpSegments/{segment_id}/businessObjectiveBasedAudiences/{audience_id}` | `dmp-segments get-predictive-audience` | read | `access-gated, private-api-gated, live-unverified` | implemented | Predictive audience read. |
| dmp-segments | list-predictive-audiences | `GET /dmpSegments/{segment_id}/businessObjectiveBasedAudiences` | `dmp-segments list-predictive-audiences` | read | `access-gated, private-api-gated, live-unverified` | implemented | Predictive audience list. |
| dmp-segments | update-predictive-audience | `POST /dmpSegments/{segment_id}/businessObjectiveBasedAudiences/{audience_id}` | `dmp-segments update-predictive-audience` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Predictive audience update. |
| dmp-segments | delete-predictive-audience | `DELETE /dmpSegments/{segment_id}/businessObjectiveBasedAudiences/{audience_id}` | `dmp-segments delete-predictive-audience` | `--apply --yes` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Predictive audience delete. |
| events | get | `GET /events/{event_id}` | `events get` | read | `access-gated, live-unverified` | implemented | Only included because Event Ads docs use it directly. |
| events | create | `POST /events` | `events create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Only included because Event Ads docs use it directly. |
| global-publisher-list | create | `POST /globalPublisherList` | `global-publisher-list create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Shared helper resource for audience restrictions. |
| inmail-contents | create | `POST /inMailContents` | `inmail-contents create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Message Ads content create. |
| inmail-contents | get | `GET /inMailContents/{inmail_content_urn}` | `inmail-contents get` | read | `access-gated, live-unverified` | implemented | Message Ads content read. |
| inmail-contents | update | `POST /inMailContents/{inmail_content_urn}` | `inmail-contents update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Message Ads content update. |
| inmail-contents | batch-get | `GET /inMailContents?ids=List(...)` | `inmail-contents batch-get` | read | `access-gated, live-unverified` | implemented | Batch read. |
| inmail-contents | send-test | `POST /inMailContents?action=sendTestInMail` | `inmail-contents send-test` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Test message send. |
| insight-tag-domains | list-by-account | `GET /insightTagDomains?q=account` | `insight-tag-domains list-by-account` | read | `access-gated, live-unverified` | implemented | Domain list. |
| insight-tag-domains | get | `GET /insightTagDomains/(account:{account_urn},domainName:{domain_name})` | `insight-tag-domains get` | read | `access-gated, live-unverified` | implemented | Single domain read. |
| insight-tag-domains | batch-get | `GET /insightTagDomains?ids=List(...)` | `insight-tag-domains batch-get` | read | `access-gated, live-unverified` | implemented | Batch domain read. |
| insight-tag-domains | upsert | `POST /insightTagDomains/(account:{account_urn},domainName:{domain_name})` | `insight-tag-domains upsert` | `--apply` | `access-gated, live-unverified` | implemented | Single domain write. |
| insight-tag-domains | batch-upsert | `POST /insightTagDomains?ids=List(...)` | `insight-tag-domains batch-upsert` | `--apply --yes` | `access-gated, live-unverified` | implemented | Batch domain write. |
| insight-tags | create | `POST /insightTags` | `insight-tags create` | `--apply` | `access-gated, live-unverified` | implemented | Insight tag create. |
| insight-tags | get | `GET /insightTags/{insight_tag_id}` | `insight-tags get` | read | `access-gated, live-unverified` | implemented | Insight tag read. |
| insight-tags | list-by-account | `GET /insightTags?q=account` | `insight-tags list-by-account` | read | `access-gated, live-unverified` | implemented | Insight tag list. |
| insight-tags | update | `POST /insightTags/{insight_tag_id}` | `insight-tags update` | `--apply` | `access-gated, live-unverified` | implemented | Insight tag update. |
| insight-tag-permissions | list-by-account | `GET /insightTagsPermission?q=account` | `insight-tag-permissions list-by-account` | read | `access-gated, live-unverified` | implemented | Permission list. |
| insight-tag-permissions | grant-access | `POST /insightTagsPermission?action=grantAccess` | `insight-tag-permissions grant-access` | `--apply --yes` | `access-gated, live-unverified` | implemented | Permission grant. |
| insight-tag-permissions | revoke-access | `POST /insightTagsPermission?action=revokeAccess` | `insight-tag-permissions revoke-access` | `--apply --yes` | `access-gated, live-unverified` | implemented | Permission revoke. |
| lead-form-responses | list-by-owner | `GET /leadFormResponses?q=owner` | `lead-form-responses list-by-owner` | read | `access-gated, live-unverified` | implemented | Lead Sync response list. |
| lead-form-responses | get | `GET /leadFormResponses/{response_id}` | `lead-form-responses get` | read | `access-gated, live-unverified` | implemented | Lead Sync response read. |
| lead-form-responses | batch-get | `GET /leadFormResponses?ids=List(...)` | `lead-form-responses batch-get` | read | `access-gated, live-unverified` | implemented | List capability is documented but example is truncated. |
| lead-forms | list-by-owner | `GET /leadForms?q=owner` | `lead-forms list-by-owner` | read | `access-gated, live-unverified` | implemented | Lead form list. |
| lead-forms | get | `GET /leadForms/{lead_form_id}` | `lead-forms get` | read | `access-gated, live-unverified` | implemented | Lead form read. |
| lead-forms | batch-get | `GET /leadForms?ids=List(...)` | `lead-forms batch-get` | read | `access-gated, live-unverified` | implemented | Batch form read. |
| lead-forms | create | `POST /leadForms` | `lead-forms create` | `--apply` | `access-gated, live-unverified` | implemented | Lead form create. |
| lead-forms | update | `POST /leadForms/{lead_form_id}` | `lead-forms update` | `--apply` | `access-gated, live-unverified` | implemented | Lead form update. |
| lead-notifications | list-by-criteria | `GET /leadNotifications?q=criteria` | `lead-notifications list-by-criteria` | read | `access-gated, live-unverified` | implemented | Lead notification list. |
| lead-notifications | get | `GET /leadNotifications/{notification_id}` | `lead-notifications get` | read | `access-gated, live-unverified` | implemented | Lead notification read. |
| lead-notifications | create | `POST /leadNotifications` | `lead-notifications create` | `--apply` | `access-gated, live-unverified` | implemented | Lead notification create. |
| lead-notifications | delete | `DELETE /leadNotifications/{notification_id}` | `lead-notifications delete` | `--apply --yes` | `access-gated, live-unverified` | implemented | Lead notification delete. |
| media-planning | forecast-reaches | `POST /mediaPlanning?action=forecastReaches` | `media-planning forecast-reaches` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private forecast action. |
| media-plans | create | `POST /mediaPlans` | `media-plans create` | `--apply` | `access-gated, private-api-gated, tier-gated, live-unverified` | implemented | Private media plan create. |
| media-plans | get | `GET /mediaPlans/{media_plan_urn}` | `media-plans get` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private media plan read. |
| media-plans | list-all | `GET /mediaPlans?q=getAllMediaPlans` | `media-plans list-all` | read | `access-gated, private-api-gated, live-unverified` | implemented | Private media plan list. |
| organizational-entity-create-share-authorizations | get | `GET /organizationalEntityCreateShareAuthorizations/owner={owner_urn}&loggedInMember={member_urn}&agent={agent_urn}` | `organizational-entity-create-share-authorizations get` | read | `access-gated, live-unverified` | implemented | Support resource for sponsored share authorizations. |
| posts | create | `POST /posts` | `posts create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Only the ad-related post path is in scope. |
| posts | get | `GET /posts/{post_urn}` | `posts get` | read | `access-gated, live-unverified` | implemented | Shared post read for ad formats. |
| posts | batch-get | `GET /posts?ids=List(...)` | `posts batch-get` | read | `access-gated, live-unverified` | implemented | Batch post read. |
| sponsored-creatives | create | `POST /creatives` | `sponsored-creatives create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Shared root creative create. |
| sponsored-creatives | create-inline | `POST /creatives?action=createInline` | `sponsored-creatives create-inline` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Inline root creative create. |
| sponsored-creatives | get | `GET /creatives/{creative_urn}` | `sponsored-creatives get` | read | `access-gated, live-unverified` | implemented | Shared root creative read. |
| sponsored-creatives | batch-get | `GET /creatives?ids=List(...)` | `sponsored-creatives batch-get` | read | `access-gated, live-unverified` | implemented | Batch root creative read. |
| sponsored-creatives | list-by-criteria | `GET /creatives?q=criteria` | `sponsored-creatives list-by-criteria` | read | `access-gated, live-unverified` | implemented | Criteria-based list. |
| sponsored-creatives | update | `POST /creatives/{creative_urn}` | `sponsored-creatives update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Shared root creative update. |
| sponsored-creatives | batch-update | `POST /creatives?ids=List(...)` | `sponsored-creatives batch-update` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch root creative update. |
| sponsored-creatives | delete | `DELETE /creatives/{creative_urn}` | `sponsored-creatives delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Shared root creative delete. |
| sponsored-creatives | batch-delete | `DELETE /creatives?ids=List(...)` | `sponsored-creatives batch-delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch root creative delete. |
| account-creatives | create | `POST /adAccounts/{ad_account_id}/creatives` | `account-creatives create` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Account-scoped creative create. |
| account-creatives | create-inline | `POST /adAccounts/{ad_account_id}/creatives?action=createInline` | `account-creatives create-inline` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Inline account-scoped creative create. |
| account-creatives | get | `GET /adAccounts/{ad_account_id}/creatives/{creative_urn}` | `account-creatives get` | read | `access-gated, live-unverified` | implemented | Path inferred because sample is truncated in docs HTML. |
| account-creatives | list-by-criteria | `GET /adAccounts/{ad_account_id}/creatives?q=criteria` | `account-creatives list-by-criteria` | read | `access-gated, live-unverified` | implemented | Criteria-based list. |
| account-creatives | batch-get | `GET /adAccounts/{ad_account_id}/creatives?ids=List(...)` | `account-creatives batch-get` | read | `access-gated, live-unverified` | implemented | Batch read. |
| account-creatives | update | `POST /adAccounts/{ad_account_id}/creatives/{creative_urn}` | `account-creatives update` | `--apply` | `access-gated, tier-gated, live-unverified` | implemented | Path inferred because sample is truncated in docs HTML. |
| account-creatives | batch-update | `POST /adAccounts/{ad_account_id}/creatives?ids=List(...)` | `account-creatives batch-update` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch update. |
| account-creatives | delete | `DELETE /adAccounts/{ad_account_id}/creatives/{creative_urn}` | `account-creatives delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Path inferred because sample is truncated in docs HTML. |
| account-creatives | batch-delete | `DELETE /adAccounts/{ad_account_id}/creatives?ids=List(...)` | `account-creatives batch-delete` | `--apply --yes` | `access-gated, tier-gated, live-unverified` | implemented | Batch delete. |
| third-party-tracking-tags | create | `POST /thirdPartyTrackingTags` | `third-party-tracking-tags create` | `--apply` | `access-gated, live-unverified` | implemented | Tracking tag create. |
| third-party-tracking-tags | get | `GET /thirdPartyTrackingTags/{tag_id}` | `third-party-tracking-tags get` | read | `access-gated, live-unverified` | implemented | Tracking tag read. |
| third-party-tracking-tags | list-by-creative | `GET /thirdPartyTrackingTags?q=creative` | `third-party-tracking-tags list-by-creative` | read | `access-gated, live-unverified` | implemented | Tracking tag list. |
| third-party-tracking-tags | delete | `DELETE /thirdPartyTrackingTags/{tag_id}` | `third-party-tracking-tags delete` | `--apply --yes` | `access-gated, live-unverified` | implemented | Tracking tag delete. |

## Explicit gaps and edge notes

- Legacy Static UTM Tracking page is not listed as a separate family.
  It reuses the `posts` resource and does not document a clean ad-only endpoint of its own. We will account for that behavior under `posts` and call out any missing live proof in `docs/proof.md`.
- Several LinkedIn HTML pages truncate example paths in code blocks.
  The current inferred paths are called out in the Notes column for `account-creatives`, `ad-target-templates`, `dmp-segments upload-list-state`, and `lead-form-responses batch-get`.
- Every row in this table is currently implemented in the shipped CLI.
  This file is the locked scope map for the current runtime and docs.
