"""Official LinkedIn Ads operation catalog.

This file is the source of truth for the implemented LinkedIn Ads CLI surface.
It captures the unique documented operations in the chosen advertising scope,
plus the gate labels we need to keep visible in docs and proof.

Last audited (UTC): 2026-05-24
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class OperationSpec:
    command: str
    method: str
    path: str
    doc_url: str
    gate_tags: tuple[str, ...]
    status: str
    safety: str
    note: str


ADS_ACCOUNTS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?view=li-lms-2026-05"
ADS_ACCOUNT_USERS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?view=li-lms-2026-05"
ADS_ACCOUNT_ACCESS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/account-access-controls?view=li-lms-2026-05"
CAMPAIGN_GROUPS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?view=li-lms-2026-05"
CAMPAIGNS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2026-05"
ACCOUNT_CREATIVES = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?view=li-lms-2026-05"
AD_PREVIEWS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/ad-preview?view=li-lms-2026-05"
AD_TARGETING = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/ads-targeting?view=li-lms-2026-05"
AUDIENCE_COUNTS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/audience-counts?view=li-lms-2026-05"
AUDIENCE_INSIGHTS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/audience-insights-api?view=li-lms-2026-05"
VIDEO_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/create-and-manage-video?view=li-lms-2026-05"
ENGAGEMENT_RETARGETING = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/engagement-retargeting?view=li-lms-2026-05"
AUDIENCE_NETWORK = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/linkedin-audience-network?view=li-lms-2026-05"
AUDIENCE_RESTRICTIONS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/manage-audience-restrictions?view=li-lms-2026-05"
SAVED_AUDIENCE_TEMPLATES = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/saved-audience-templates?view=li-lms-2026-05"
ARTICLE_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/article-ads-integrations?view=li-lms-2026-05"
CAROUSEL_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/carousel-ads-integrations?view=li-lms-2026-05"
CONVERSATION_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/conversation-ads-integrations?view=li-lms-2026-05"
DOCUMENT_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/document-ads?view=li-lms-2026-05"
EVENT_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/event-ads-integrations?view=li-lms-2026-05"
FOLLOWER_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/follower-ads?view=li-lms-2026-05"
IMAGE_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/image-ads-integrations?view=li-lms-2026-05"
JOBS_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/jobs-ads-integrations?view=li-lms-2026-05"
MESSAGE_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/message-ads-integrations?view=li-lms-2026-05"
SPOTLIGHT_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/spotlight-ads?view=li-lms-2026-05"
TEXT_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/text-ads-integrations?view=li-lms-2026-05"
VAST_VIDEO_ADS = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/vast-tag-video-ads-api?view=li-lms-2026-05"
ADS_REPORTING = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?view=li-lms-2026-05"
AD_BUDGET_PRICING = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ad-budget-pricing?view=li-lms-2026-05"
CONVERSION_TRACKING = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking?view=li-lms-2026-05"
CONVERSIONS_API = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversions-api?view=li-lms-2026-05"
DYNAMIC_UTM = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/dynamic-utm-tracking?view=li-lms-2026-05"
THIRD_PARTY_TRACKING = "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/third-party-tracking?view=li-lms-2026-05"
COMPANY_INTEL = "https://learn.microsoft.com/en-us/linkedin/marketing/account-intel/account-intel-api?view=li-lms-2026-05"
LEAD_SYNC = "https://learn.microsoft.com/en-us/linkedin/marketing/lead-sync/leadsync?view=li-lms-2026-05"
AD_SEGMENTS = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/adsegments?view=li-lms-2026-05"
SEGMENT_UPLOADS = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/create-and-manage-list-uploads?view=li-lms-2026-05"
SEGMENT_COMPANIES = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/create-and-manage-segment-companies?view=li-lms-2026-05"
SEGMENT_DESTINATIONS = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/create-and-manage-segment-destinations?view=li-lms-2026-05"
SEGMENT_USERS = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/create-and-manage-segment-users?view=li-lms-2026-05"
SEGMENTS = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/create-and-manage-segments?view=li-lms-2026-05"
MATCHED_AUDIENCES = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/matched-audiences?view=li-lms-2026-05"
PREDICTIVE_AUDIENCES = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/predictive-audiences?view=li-lms-2026-05"
WEBSITE_RETARGETING = "https://learn.microsoft.com/en-us/linkedin/marketing/matched-audiences/website-visitors-retargeting?view=li-lms-2026-05"
MEDIA_PLANS = "https://learn.microsoft.com/en-us/linkedin/marketing/media-planning/media-plan?view=li-lms-2026-05"
MEDIA_PLANNING = "https://learn.microsoft.com/en-us/linkedin/marketing/media-planning/media-planning-api?view=li-lms-2026-05"

BASE_READ = ("access-gated", "live-unverified")
BASE_WRITE = ("access-gated", "tier-gated", "live-unverified")
PRIVATE_READ = ("access-gated", "private-api-gated", "live-unverified")
PRIVATE_WRITE = ("access-gated", "private-api-gated", "tier-gated", "live-unverified")
LEAD_SYNC_GATE = ("access-gated", "live-unverified")

READ = "read"
WRITE = "write-apply"
RISKY = "write-apply-yes"


OPERATIONS_BY_FAMILY: Final[dict[str, tuple[OperationSpec, ...]]] = {
    "account-intelligence": (
        OperationSpec("get-account-intelligence", "GET", "/accountIntelligence?q=account", COMPANY_INTEL, PRIVATE_READ, "implemented", READ, "Private Company Intelligence search for one sponsored account."),
    ),
    "ad-account-trust-preferences": (
        OperationSpec("get", "GET", "/adAccountTrustPreferences/{sponsored_account_id}", AUDIENCE_RESTRICTIONS, BASE_READ, "implemented", READ, "Read audience trust settings for one ad account."),
        OperationSpec("update", "PUT", "/adAccountTrustPreferences/{sponsored_account_id}", AUDIENCE_RESTRICTIONS, BASE_WRITE, "implemented", WRITE, "Update trust preferences tied to audience restrictions."),
    ),
    "ad-account-users": (
        OperationSpec("set-role", "PUT", "/adAccountUsers/(account:{account_urn},user:{person_urn})", ADS_ACCOUNT_USERS, BASE_WRITE, "implemented", RISKY, "Create or replace one ad-account user binding."),
        OperationSpec("update-role", "POST", "/adAccountUsers/(account:{account_urn},user:{person_urn})", ADS_ACCOUNT_USERS, BASE_WRITE, "implemented", RISKY, "Partial update for one ad-account user binding."),
        OperationSpec("get", "GET", "/adAccountUsers/(account:{account_urn},user:{person_urn})", ADS_ACCOUNT_USERS, BASE_READ, "implemented", READ, "Get one ad-account user binding."),
        OperationSpec("list-authenticated-user", "GET", "/adAccountUsers?q=authenticatedUser", ADS_ACCOUNT_USERS, BASE_READ, "implemented", READ, "List ad-account roles for the signed-in member."),
        OperationSpec("list-by-account", "GET", "/adAccountUsers?q=accounts", ADS_ACCOUNT_USERS, BASE_READ, "implemented", READ, "List ad-account users for one sponsored account."),
        OperationSpec("delete", "DELETE", "/adAccountUsers/(account:{account_urn},user:{person_urn})", ADS_ACCOUNT_USERS, BASE_WRITE, "implemented", RISKY, "Remove one ad-account user binding."),
    ),
    "ad-accounts": (
        OperationSpec("create", "POST", "/adAccounts", ADS_ACCOUNTS, BASE_WRITE, "implemented", WRITE, "Create an ad account. Standard-tier access is needed for broad live use."),
        OperationSpec("get", "GET", "/adAccounts/{ad_account_id}", ADS_ACCOUNTS, BASE_READ, "implemented", READ, "Get one ad account."),
        OperationSpec("update", "POST", "/adAccounts/{ad_account_id}", ADS_ACCOUNTS, BASE_WRITE, "implemented", WRITE, "Update one ad account."),
        OperationSpec("delete", "DELETE", "/adAccounts/{ad_account_id}", ADS_ACCOUNTS, BASE_WRITE, "implemented", RISKY, "Delete one ad account."),
        OperationSpec("search", "GET", "/adAccounts?q=search", ADS_ACCOUNTS, BASE_READ, "implemented", READ, "Search ad accounts with rest.li search criteria."),
    ),
    "ad-campaign-groups": (
        OperationSpec("create", "POST", "/adAccounts/{ad_account_id}/adCampaignGroups", CAMPAIGN_GROUPS, BASE_WRITE, "implemented", WRITE, "Create one campaign group."),
        OperationSpec("get", "GET", "/adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}", CAMPAIGN_GROUPS, BASE_READ, "implemented", READ, "Get one campaign group."),
        OperationSpec("search", "GET", "/adAccounts/{ad_account_id}/adCampaignGroups?q=search", CAMPAIGN_GROUPS, BASE_READ, "implemented", READ, "Search campaign groups for one account."),
        OperationSpec("batch-get", "GET", "/adAccounts/{ad_account_id}/adCampaignGroups?ids=List(...)", CAMPAIGN_GROUPS, BASE_READ, "implemented", READ, "Batch get campaign groups by ids."),
        OperationSpec("update", "POST", "/adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}", CAMPAIGN_GROUPS, BASE_WRITE, "implemented", WRITE, "Update one campaign group."),
        OperationSpec("batch-update", "POST", "/adAccounts/{ad_account_id}/adCampaignGroups?ids=List(...)", CAMPAIGN_GROUPS, BASE_WRITE, "implemented", RISKY, "Batch update campaign groups by ids."),
        OperationSpec("delete", "DELETE", "/adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}", CAMPAIGN_GROUPS, BASE_WRITE, "implemented", RISKY, "Delete one campaign group."),
        OperationSpec("batch-delete", "DELETE", "/adAccounts/{ad_account_id}/adCampaignGroups?ids=List(...)", CAMPAIGN_GROUPS, BASE_WRITE, "implemented", RISKY, "Batch delete campaign groups by ids."),
    ),
    "ad-campaigns": (
        OperationSpec("create", "POST", "/adAccounts/{ad_account_id}/adCampaigns", CAMPAIGNS, BASE_WRITE, "implemented", WRITE, "Create one campaign."),
        OperationSpec("get", "GET", "/adAccounts/{ad_account_id}/adCampaigns/{campaign_id}", CAMPAIGNS, BASE_READ, "implemented", READ, "Get one campaign."),
        OperationSpec("search", "GET", "/adAccounts/{ad_account_id}/adCampaigns?q=search", CAMPAIGNS, BASE_READ, "implemented", READ, "Search campaigns with rest.li search criteria."),
        OperationSpec("batch-get", "GET", "/adAccounts/{ad_account_id}/adCampaigns?ids=List(...)", CAMPAIGNS, BASE_READ, "implemented", READ, "Batch get campaigns by ids."),
        OperationSpec("update", "POST", "/adAccounts/{ad_account_id}/adCampaigns/{campaign_id}", CAMPAIGNS, BASE_WRITE, "implemented", WRITE, "Update one campaign."),
        OperationSpec("delete", "DELETE", "/adAccounts/{ad_account_id}/adCampaigns/{campaign_id}", CAMPAIGNS, BASE_WRITE, "implemented", RISKY, "Delete one campaign."),
    ),
    "ad-analytics": (
        OperationSpec("analytics", "GET", "/adAnalytics?q=analytics", ADS_REPORTING, BASE_READ, "implemented", READ, "Analytics query with one pivot and time granularity."),
        OperationSpec("statistics", "GET", "/adAnalytics?q=statistics", ADS_REPORTING, BASE_READ, "implemented", READ, "Statistics query with one or more pivots."),
        OperationSpec("attributed-revenue-metrics", "GET", "/adAnalytics?q=attributedRevenueMetrics", ADS_REPORTING, BASE_READ, "implemented", READ, "Attributed revenue metrics query."),
    ),
    "ad-budget-pricing": (
        OperationSpec("forecast-price", "GET", "/adBudgetPricing?q=criteriaV2", AD_BUDGET_PRICING, BASE_READ, "implemented", READ, "Estimate bid and budget guidance for targeting criteria."),
    ),
    "ad-page-sets": (
        OperationSpec("create", "POST", "/adPageSets", SEGMENT_UPLOADS, PRIVATE_WRITE, "implemented", WRITE, "Create a page set for website retargeting."),
    ),
    "ad-previews": (
        OperationSpec("get-by-creative", "GET", "/adPreviews?q=creative", AD_PREVIEWS, BASE_READ, "implemented", READ, "Fetch preview metadata for one creative."),
        OperationSpec("live-preview-for-creative", "POST", "/adPreviews?action=livePreviewForCreative", AD_PREVIEWS, BASE_READ, "implemented", READ, "Generate a live preview from an existing creative."),
        OperationSpec("live-preview-for-creative-inline", "POST", "/adPreviews?action=livePreviewForCreativeInline", AD_PREVIEWS, BASE_READ, "implemented", READ, "Generate a live preview from an inline creative payload."),
    ),
    "ad-publisher-restrictions": (
        OperationSpec("get", "GET", "/adPublisherRestrictions/{restriction_id}", AUDIENCE_RESTRICTIONS, BASE_READ, "implemented", READ, "Get one publisher restriction bundle."),
        OperationSpec("list-by-entity", "GET", "/adPublisherRestrictions?q=entity", AUDIENCE_RESTRICTIONS, BASE_READ, "implemented", READ, "List publisher restrictions for an account or campaign."),
        OperationSpec("create", "POST", "/adPublisherRestrictions", AUDIENCE_RESTRICTIONS, BASE_WRITE, "implemented", WRITE, "Create or replace publisher restriction configuration."),
        OperationSpec("generate-download-url", "POST", "/adPublisherRestrictions?action=generateRestrictionsDownloadUrl", AUDIENCE_RESTRICTIONS, BASE_READ, "implemented", READ, "Generate a download URL for publisher restrictions."),
        OperationSpec("generate-upload-url", "POST", "/adPublisherRestrictions?action=generateRestrictionsUploadUrl", AUDIENCE_RESTRICTIONS, BASE_READ, "implemented", READ, "Generate an upload URL for publisher restrictions."),
    ),
    "ad-segment-sources": (
        OperationSpec("associate", "PUT", "/adSegmentSources/source={ad_page_set_urn}&segment={ad_segment_urn}", WEBSITE_RETARGETING, PRIVATE_WRITE, "implemented", WRITE, "Attach a page set source to an ad segment."),
        OperationSpec("delete-association", "DELETE", "/adSegmentSources/source={ad_page_set_urn}&segment={ad_segment_urn}", WEBSITE_RETARGETING, PRIVATE_WRITE, "implemented", RISKY, "Remove a page set source from an ad segment."),
    ),
    "ad-segments": (
        OperationSpec("get", "GET", "/adSegments/{segment_id}", AD_SEGMENTS, PRIVATE_READ, "implemented", READ, "Get one ad segment."),
        OperationSpec("update", "POST", "/adSegments/{segment_id}", AD_SEGMENTS, PRIVATE_WRITE, "implemented", WRITE, "Update one ad segment."),
        OperationSpec("list-by-account", "GET", "/adSegments?q=accounts", MATCHED_AUDIENCES, PRIVATE_READ, "implemented", READ, "List ad segments for one sponsored account."),
    ),
    "ad-supply-forecasts": (
        OperationSpec("forecast", "GET", "/adSupplyForecasts?q=criteriaV2", "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/ad-supply-forecasts?view=li-lms-2026-05", BASE_READ, "implemented", READ, "Forecast available supply for targeting and budgets."),
    ),
    "ad-target-templates": (
        OperationSpec("create", "POST", "/adTargetTemplates", SAVED_AUDIENCE_TEMPLATES, BASE_WRITE, "implemented", WRITE, "Create a saved audience template."),
        OperationSpec("get", "GET", "/adTargetTemplates/{template_id}", SAVED_AUDIENCE_TEMPLATES, BASE_READ, "implemented", READ, "Get one saved audience template. Docs show a trailing slash path; this path is inferred."),
        OperationSpec("update", "POST", "/adTargetTemplates/{template_id}", SAVED_AUDIENCE_TEMPLATES, BASE_WRITE, "implemented", WRITE, "Update one saved audience template. Docs show a trailing slash path; this path is inferred."),
        OperationSpec("delete", "DELETE", "/adTargetTemplates/{template_id}", SAVED_AUDIENCE_TEMPLATES, BASE_WRITE, "implemented", RISKY, "Delete one saved audience template. Docs show a trailing slash path; this path is inferred."),
        OperationSpec("batch-delete", "DELETE", "/adTargetTemplates?ids=List(...)", SAVED_AUDIENCE_TEMPLATES, BASE_WRITE, "implemented", RISKY, "Batch delete saved audience templates."),
        OperationSpec("list-by-account", "GET", "/adTargetTemplates?q=account", SAVED_AUDIENCE_TEMPLATES, BASE_READ, "implemented", READ, "List saved audience templates for one account."),
    ),
    "ad-targeting-entities": (
        OperationSpec("list-by-facet", "GET", "/adTargetingEntities?q=adTargetingFacet", AD_TARGETING, BASE_READ, "implemented", READ, "List targeting entities for one facet."),
        OperationSpec("similar-entities", "GET", "/adTargetingEntities?q=similarEntities", AD_TARGETING, BASE_READ, "implemented", READ, "Find targeting entities similar to known entities."),
        OperationSpec("typeahead", "GET", "/adTargetingEntities?q=typeahead", AD_TARGETING, BASE_READ, "implemented", READ, "Typeahead search for targeting entities."),
        OperationSpec("get-by-urns", "GET", "/adTargetingEntities?q=urns", AD_TARGETING, BASE_READ, "implemented", READ, "Resolve targeting entities by URN list."),
    ),
    "ad-targeting-facets": (
        OperationSpec("list", "GET", "/adTargetingFacets", AD_TARGETING, BASE_READ, "implemented", READ, "List supported targeting facets."),
    ),
    "ad-tracking-parameters": (
        OperationSpec("upsert-for-campaign", "PUT", "/adTrackingParameters/(adEntity:(sponsoredCampaign:{campaign_urn}))", DYNAMIC_UTM, BASE_WRITE, "implemented", WRITE, "Create or update dynamic UTM tracking for a campaign."),
        OperationSpec("get-for-campaign", "GET", "/adTrackingParameters/(adEntity:(sponsoredCampaign:{campaign_urn}))", DYNAMIC_UTM, BASE_READ, "implemented", READ, "Get dynamic UTM tracking for a campaign."),
        OperationSpec("delete-for-campaign", "DELETE", "/adTrackingParameters/(adEntity:(sponsoredCampaign:{campaign_urn}))", DYNAMIC_UTM, BASE_WRITE, "implemented", RISKY, "Delete dynamic UTM tracking for a campaign."),
    ),
    "audience-counts": (
        OperationSpec("estimate", "GET", "/audienceCounts?q=targetingCriteriaV2", AUDIENCE_COUNTS, BASE_READ, "implemented", READ, "Estimate audience size for targeting criteria."),
    ),
    "audience-insights": (
        OperationSpec("audience-insights", "POST", "/targetingAudienceInsights?action=audienceInsights", AUDIENCE_INSIGHTS, PRIVATE_READ, "implemented", READ, "Run private audience insights analysis."),
    ),
    "campaign-conversions": (
        OperationSpec("associate", "PUT", "/campaignConversions/(campaign:{campaign_urn},conversion:{conversion_urn})", CONVERSION_TRACKING, BASE_WRITE, "implemented", WRITE, "Associate one conversion with one campaign."),
        OperationSpec("batch-associate", "PUT", "/campaignConversions?ids=List(...)", CONVERSIONS_API, BASE_WRITE, "implemented", RISKY, "Batch associate conversions with campaigns."),
        OperationSpec("get", "GET", "/campaignConversions/(campaign:{campaign_urn},conversion:{conversion_urn})", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Get one campaign-conversion association."),
        OperationSpec("batch-get", "GET", "/campaignConversions?ids=List(...)", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Batch get campaign-conversion associations."),
        OperationSpec("list-by-campaigns", "GET", "/campaignConversions?q=campaigns", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "List campaign-conversion associations for campaigns."),
        OperationSpec("delete", "DELETE", "/campaignConversions/(campaign:{campaign_urn},conversion:{conversion_urn})", CONVERSION_TRACKING, BASE_WRITE, "implemented", RISKY, "Delete one campaign-conversion association."),
        OperationSpec("batch-delete", "DELETE", "/campaignConversions?ids=List(...)", CONVERSION_TRACKING, BASE_WRITE, "implemented", RISKY, "Batch delete campaign-conversion associations."),
    ),
    "conversation-ads": (
        OperationSpec("create", "POST", "/conversationAds", CONVERSATION_ADS, BASE_WRITE, "implemented", WRITE, "Create one conversation ad shell."),
        OperationSpec("get", "GET", "/conversationAds/{conversation_urn}", CONVERSATION_ADS, BASE_READ, "implemented", READ, "Get one conversation ad."),
        OperationSpec("update", "POST", "/conversationAds/{conversation_urn}", CONVERSATION_ADS, BASE_WRITE, "implemented", WRITE, "Update one conversation ad."),
        OperationSpec("batch-get", "GET", "/conversationAds?ids=List(...)", CONVERSATION_ADS, BASE_READ, "implemented", READ, "Batch get conversation ads by URN."),
        OperationSpec("create-sponsored-message-content", "POST", "/conversationAds/{conversation_urn}/sponsoredMessageContents", CONVERSATION_ADS, BASE_WRITE, "implemented", WRITE, "Create one sponsored message node."),
        OperationSpec("get-sponsored-message-content", "GET", "/conversationAds/{conversation_urn}/sponsoredMessageContents/{message_urn}", CONVERSATION_ADS, BASE_READ, "implemented", READ, "Get one sponsored message node."),
        OperationSpec("list-sponsored-message-contents", "GET", "/conversationAds/{conversation_urn}/sponsoredMessageContents", CONVERSATION_ADS, BASE_READ, "implemented", READ, "List sponsored message nodes for one conversation ad."),
        OperationSpec("update-sponsored-message-content", "POST", "/conversationAds/{conversation_urn}/sponsoredMessageContents/{message_urn}", CONVERSATION_ADS, BASE_WRITE, "implemented", WRITE, "Update one sponsored message node."),
        OperationSpec("batch-update-sponsored-message-contents", "POST", "/conversationAds/{conversation_urn}/sponsoredMessageContents?ids=List(...)", CONVERSATION_ADS, BASE_WRITE, "implemented", RISKY, "Batch update sponsored message nodes."),
        OperationSpec("batch-delete-sponsored-message-contents", "DELETE", "/conversationAds/{conversation_urn}/sponsoredMessageContents?ids=List(...)", CONVERSATION_ADS, BASE_WRITE, "implemented", RISKY, "Batch delete sponsored message nodes."),
    ),
    "conversion-events": (
        OperationSpec("create", "POST", "/conversionEvents", CONVERSIONS_API, BASE_WRITE, "implemented", WRITE, "Send one or more conversion events."),
    ),
    "conversions": (
        OperationSpec("create", "POST", "/conversions", CONVERSION_TRACKING, BASE_WRITE, "implemented", WRITE, "Create one conversion definition."),
        OperationSpec("get", "GET", "/conversions/{conversion_id}", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Get one conversion definition."),
        OperationSpec("batch-get", "GET", "/conversions?ids=List(...)", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Batch get conversions by ids."),
        OperationSpec("list-by-account", "GET", "/conversions?q=account", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "List conversions for one account."),
        OperationSpec("update", "POST", "/conversions/{conversion_id}", CONVERSION_TRACKING, BASE_WRITE, "implemented", WRITE, "Update one conversion definition."),
        OperationSpec("batch-update", "POST", "/conversions?ids=List(...)", CONVERSION_TRACKING, BASE_WRITE, "implemented", RISKY, "Batch update conversion definitions."),
    ),
    "dmp-engagement-source-types": (
        OperationSpec("list", "GET", "/dmpEngagementSourceTypes", ENGAGEMENT_RETARGETING, PRIVATE_READ, "implemented", READ, "List engagement retargeting source types."),
        OperationSpec("get", "GET", "/dmpEngagementSourceTypes/{source_type}", ENGAGEMENT_RETARGETING, PRIVATE_READ, "implemented", READ, "Get one engagement source type."),
        OperationSpec("list-triggers", "GET", "/dmpEngagementSourceTypes/{source_type}/dmpEngagementTriggers", ENGAGEMENT_RETARGETING, PRIVATE_READ, "implemented", READ, "List triggers for one engagement source type."),
        OperationSpec("get-trigger", "GET", "/dmpEngagementSourceTypes/{source_type}/dmpEngagementTriggers/{trigger_id}", ENGAGEMENT_RETARGETING, PRIVATE_READ, "implemented", READ, "Get one engagement trigger."),
    ),
    "dmp-segments": (
        OperationSpec("create", "POST", "/dmpSegments", SEGMENTS, PRIVATE_WRITE, "implemented", WRITE, "Create one DMP segment."),
        OperationSpec("get", "GET", "/dmpSegments/{segment_id}", SEGMENTS, PRIVATE_READ, "implemented", READ, "Get one DMP segment."),
        OperationSpec("batch-get", "GET", "/dmpSegments?ids=List(...)", SEGMENTS, PRIVATE_READ, "implemented", READ, "Batch get DMP segments by ids."),
        OperationSpec("list-by-account", "GET", "/dmpSegments?q=account", SEGMENTS, PRIVATE_READ, "implemented", READ, "List DMP segments for one account."),
        OperationSpec("update", "POST", "/dmpSegments/{segment_id}", SEGMENTS, PRIVATE_WRITE, "implemented", WRITE, "Update one DMP segment."),
        OperationSpec("delete", "DELETE", "/dmpSegments/{segment_id}", SEGMENTS, PRIVATE_WRITE, "implemented", RISKY, "Delete one DMP segment."),
        OperationSpec("batch-delete", "DELETE", "/dmpSegments?ids=List(...)", SEGMENTS, PRIVATE_WRITE, "implemented", RISKY, "Batch delete DMP segments by ids."),
        OperationSpec("generate-upload-url", "POST", "/dmpSegments?action=generateUploadUrl", SEGMENT_UPLOADS, PRIVATE_READ, "implemented", READ, "Generate an upload URL for list uploads."),
        OperationSpec("upload-list-state", "POST", "/dmpSegments/{segment_id}", SEGMENT_UPLOADS, PRIVATE_WRITE, "implemented", WRITE, "Update list-upload metadata or status. Docs truncate the sample path; this path is inferred."),
        OperationSpec("create-engagement-rule", "POST", "/dmpSegments/{segment_id}/engagementRules", ENGAGEMENT_RETARGETING, PRIVATE_WRITE, "implemented", WRITE, "Create one engagement retargeting rule."),
        OperationSpec("get-engagement-rule", "GET", "/dmpSegments/{segment_id}/engagementRules/{rule_id}", ENGAGEMENT_RETARGETING, PRIVATE_READ, "implemented", READ, "Get one engagement retargeting rule."),
        OperationSpec("list-engagement-rules", "GET", "/dmpSegments/{segment_id}/engagementRules", ENGAGEMENT_RETARGETING, PRIVATE_READ, "implemented", READ, "List engagement retargeting rules."),
        OperationSpec("delete-engagement-rule", "DELETE", "/dmpSegments/{segment_id}/engagementRules/{rule_id}", ENGAGEMENT_RETARGETING, PRIVATE_WRITE, "implemented", RISKY, "Delete one engagement retargeting rule."),
        OperationSpec("batch-delete-engagement-rules", "DELETE", "/dmpSegments/{segment_id}/engagementRules?ids=List(...)", ENGAGEMENT_RETARGETING, PRIVATE_WRITE, "implemented", RISKY, "Batch delete engagement retargeting rules."),
        OperationSpec("create-company-match", "POST", "/dmpSegments/{segment_id}/companies", SEGMENT_COMPANIES, PRIVATE_WRITE, "implemented", WRITE, "Upload company match data for one segment."),
        OperationSpec("create-user-match", "POST", "/dmpSegments/{segment_id}/users", SEGMENT_USERS, PRIVATE_WRITE, "implemented", WRITE, "Upload user match data for one segment."),
        OperationSpec("create-destination", "POST", "/dmpSegments/{segment_id}/destinations", SEGMENT_DESTINATIONS, PRIVATE_WRITE, "implemented", WRITE, "Create one segment destination."),
        OperationSpec("get-destination", "GET", "/dmpSegments/{segment_id}/destinations/{destination_id}", SEGMENT_DESTINATIONS, PRIVATE_READ, "implemented", READ, "Get one segment destination."),
        OperationSpec("list-destinations", "GET", "/dmpSegments/{segment_id}/destinations", SEGMENT_DESTINATIONS, PRIVATE_READ, "implemented", READ, "List destinations for one segment."),
        OperationSpec("create-predictive-audience", "POST", "/dmpSegments/{segment_id}/businessObjectiveBasedAudiences", PREDICTIVE_AUDIENCES, PRIVATE_WRITE, "implemented", WRITE, "Create one predictive audience."),
        OperationSpec("get-predictive-audience", "GET", "/dmpSegments/{segment_id}/businessObjectiveBasedAudiences/{audience_id}", PREDICTIVE_AUDIENCES, PRIVATE_READ, "implemented", READ, "Get one predictive audience."),
        OperationSpec("list-predictive-audiences", "GET", "/dmpSegments/{segment_id}/businessObjectiveBasedAudiences", PREDICTIVE_AUDIENCES, PRIVATE_READ, "implemented", READ, "List predictive audiences for one segment."),
        OperationSpec("update-predictive-audience", "POST", "/dmpSegments/{segment_id}/businessObjectiveBasedAudiences/{audience_id}", PREDICTIVE_AUDIENCES, PRIVATE_WRITE, "implemented", WRITE, "Update one predictive audience."),
        OperationSpec("delete-predictive-audience", "DELETE", "/dmpSegments/{segment_id}/businessObjectiveBasedAudiences/{audience_id}", PREDICTIVE_AUDIENCES, PRIVATE_WRITE, "implemented", RISKY, "Delete one predictive audience."),
    ),
    "events": (
        OperationSpec("get", "GET", "/events/{event_id}", EVENT_ADS, BASE_READ, "implemented", READ, "Get one event used by Event Ads."),
        OperationSpec("create", "POST", "/events", EVENT_ADS, BASE_WRITE, "implemented", WRITE, "Create one event for Event Ads flows."),
    ),
    "global-publisher-list": (
        OperationSpec("create", "POST", "/globalPublisherList", AUDIENCE_RESTRICTIONS, BASE_WRITE, "implemented", WRITE, "Create a global publisher list file reference."),
    ),
    "inmail-contents": (
        OperationSpec("create", "POST", "/inMailContents", MESSAGE_ADS, BASE_WRITE, "implemented", WRITE, "Create one message ad content record."),
        OperationSpec("get", "GET", "/inMailContents/{inmail_content_urn}", MESSAGE_ADS, BASE_READ, "implemented", READ, "Get one message ad content record."),
        OperationSpec("update", "POST", "/inMailContents/{inmail_content_urn}", MESSAGE_ADS, BASE_WRITE, "implemented", WRITE, "Update one message ad content record."),
        OperationSpec("batch-get", "GET", "/inMailContents?ids=List(...)", MESSAGE_ADS, BASE_READ, "implemented", READ, "Batch get message ad content records."),
        OperationSpec("send-test", "POST", "/inMailContents?action=sendTestInMail", MESSAGE_ADS, BASE_WRITE, "implemented", WRITE, "Send a test message ad."),
    ),
    "insight-tag-domains": (
        OperationSpec("list-by-account", "GET", "/insightTagDomains?q=account", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "List domains for one insight tag account."),
        OperationSpec("get", "GET", "/insightTagDomains/(account:{account_urn},domainName:{domain_name})", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Get one tracked domain."),
        OperationSpec("batch-get", "GET", "/insightTagDomains?ids=List(...)", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Batch get tracked domains."),
        OperationSpec("upsert", "POST", "/insightTagDomains/(account:{account_urn},domainName:{domain_name})", CONVERSION_TRACKING, BASE_WRITE, "implemented", WRITE, "Create or update one tracked domain."),
        OperationSpec("batch-upsert", "POST", "/insightTagDomains?ids=List(...)", CONVERSION_TRACKING, BASE_WRITE, "implemented", RISKY, "Batch create or update tracked domains."),
    ),
    "insight-tags": (
        OperationSpec("create", "POST", "/insightTags", CONVERSION_TRACKING, BASE_WRITE, "implemented", WRITE, "Create one insight tag."),
        OperationSpec("get", "GET", "/insightTags/{insight_tag_id}", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "Get one insight tag."),
        OperationSpec("list-by-account", "GET", "/insightTags?q=account", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "List insight tags for one account."),
        OperationSpec("update", "POST", "/insightTags/{insight_tag_id}", CONVERSION_TRACKING, BASE_WRITE, "implemented", WRITE, "Update one insight tag."),
    ),
    "insight-tag-permissions": (
        OperationSpec("list-by-account", "GET", "/insightTagsPermission?q=account", CONVERSION_TRACKING, BASE_READ, "implemented", READ, "List insight tag sharing permissions for one account."),
        OperationSpec("grant-access", "POST", "/insightTagsPermission?action=grantAccess", CONVERSION_TRACKING, BASE_WRITE, "implemented", RISKY, "Grant insight tag access to another account."),
        OperationSpec("revoke-access", "POST", "/insightTagsPermission?action=revokeAccess", CONVERSION_TRACKING, BASE_WRITE, "implemented", RISKY, "Revoke shared insight tag access."),
    ),
    "lead-form-responses": (
        OperationSpec("list-by-owner", "GET", "/leadFormResponses?q=owner", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "List lead form responses for one owner and form."),
        OperationSpec("get", "GET", "/leadFormResponses/{response_id}", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "Get one lead form response."),
        OperationSpec("batch-get", "GET", "/leadFormResponses?ids=List(...)", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "Batch get lead form responses. The ids sample is truncated in docs but the list capability is documented."),
    ),
    "lead-forms": (
        OperationSpec("list-by-owner", "GET", "/leadForms?q=owner", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "List lead forms for one owner."),
        OperationSpec("get", "GET", "/leadForms/{lead_form_id}", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "Get one lead form."),
        OperationSpec("batch-get", "GET", "/leadForms?ids=List(...)", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "Batch get lead forms."),
        OperationSpec("create", "POST", "/leadForms", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", WRITE, "Create one lead form."),
        OperationSpec("update", "POST", "/leadForms/{lead_form_id}", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", WRITE, "Update one lead form."),
    ),
    "lead-notifications": (
        OperationSpec("list-by-criteria", "GET", "/leadNotifications?q=criteria", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "List lead notifications for one owner or lead type."),
        OperationSpec("get", "GET", "/leadNotifications/{notification_id}", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", READ, "Get one lead notification."),
        OperationSpec("create", "POST", "/leadNotifications", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", WRITE, "Create one lead notification subscription."),
        OperationSpec("delete", "DELETE", "/leadNotifications/{notification_id}", LEAD_SYNC, LEAD_SYNC_GATE, "implemented", RISKY, "Delete one lead notification subscription."),
    ),
    "media-planning": (
        OperationSpec("forecast-reaches", "POST", "/mediaPlanning?action=forecastReaches", MEDIA_PLANNING, PRIVATE_READ, "implemented", READ, "Run private media planning reach forecasts."),
    ),
    "media-plans": (
        OperationSpec("create", "POST", "/mediaPlans", MEDIA_PLANS, PRIVATE_WRITE, "implemented", WRITE, "Create one media plan."),
        OperationSpec("get", "GET", "/mediaPlans/{media_plan_urn}", MEDIA_PLANS, PRIVATE_READ, "implemented", READ, "Get one media plan."),
        OperationSpec("list-all", "GET", "/mediaPlans?q=getAllMediaPlans", MEDIA_PLANS, PRIVATE_READ, "implemented", READ, "List media plans for one account."),
    ),
    "organizational-entity-create-share-authorizations": (
        OperationSpec("get", "GET", "/organizationalEntityCreateShareAuthorizations/owner={owner_urn}&loggedInMember={member_urn}&agent={agent_urn}", ADS_ACCOUNT_ACCESS, BASE_READ, "implemented", READ, "Check whether an account can create sponsored shares for an organization."),
    ),
    "posts": (
        OperationSpec("create", "POST", "/posts", ARTICLE_ADS, BASE_WRITE, "implemented", WRITE, "Create one post asset used by ad formats such as article, image, document, video, or event ads."),
        OperationSpec("get", "GET", "/posts/{post_urn}", ARTICLE_ADS, BASE_READ, "implemented", READ, "Get one post asset used by ads."),
        OperationSpec("batch-get", "GET", "/posts?ids=List(...)", CAROUSEL_ADS, BASE_READ, "implemented", READ, "Batch get post assets."),
    ),
    "sponsored-creatives": (
        OperationSpec("create", "POST", "/creatives", FOLLOWER_ADS, BASE_WRITE, "implemented", WRITE, "Create one root creative for text, follower, spotlight, jobs, or VAST video ads."),
        OperationSpec("create-inline", "POST", "/creatives?action=createInline", ARTICLE_ADS, BASE_WRITE, "implemented", WRITE, "Create one root creative with inline payload."),
        OperationSpec("get", "GET", "/creatives/{creative_urn}", FOLLOWER_ADS, BASE_READ, "implemented", READ, "Get one root creative."),
        OperationSpec("batch-get", "GET", "/creatives?ids=List(...)", FOLLOWER_ADS, BASE_READ, "implemented", READ, "Batch get root creatives."),
        OperationSpec("list-by-criteria", "GET", "/creatives?q=criteria", FOLLOWER_ADS, BASE_READ, "implemented", READ, "List root creatives by campaign or status filters."),
        OperationSpec("update", "POST", "/creatives/{creative_urn}", FOLLOWER_ADS, BASE_WRITE, "implemented", WRITE, "Update one root creative."),
        OperationSpec("batch-update", "POST", "/creatives?ids=List(...)", TEXT_ADS, BASE_WRITE, "implemented", RISKY, "Batch update root creatives."),
        OperationSpec("delete", "DELETE", "/creatives/{creative_urn}", FOLLOWER_ADS, BASE_WRITE, "implemented", RISKY, "Delete one root creative."),
        OperationSpec("batch-delete", "DELETE", "/creatives?ids=List(...)", TEXT_ADS, BASE_WRITE, "implemented", RISKY, "Batch delete root creatives."),
    ),
    "account-creatives": (
        OperationSpec("create", "POST", "/adAccounts/{ad_account_id}/creatives", ACCOUNT_CREATIVES, BASE_WRITE, "implemented", WRITE, "Create one account-scoped creative."),
        OperationSpec("create-inline", "POST", "/adAccounts/{ad_account_id}/creatives?action=createInline", ACCOUNT_CREATIVES, BASE_WRITE, "implemented", WRITE, "Create one account-scoped creative from inline data."),
        OperationSpec("get", "GET", "/adAccounts/{ad_account_id}/creatives/{creative_urn}", ACCOUNT_CREATIVES, BASE_READ, "implemented", READ, "Get one account-scoped creative. The docs sample path is partially truncated; this path is inferred from the documented examples."),
        OperationSpec("list-by-criteria", "GET", "/adAccounts/{ad_account_id}/creatives?q=criteria", ACCOUNT_CREATIVES, BASE_READ, "implemented", READ, "List account-scoped creatives with criteria filters."),
        OperationSpec("batch-get", "GET", "/adAccounts/{ad_account_id}/creatives?ids=List(...)", ACCOUNT_CREATIVES, BASE_READ, "implemented", READ, "Batch get account-scoped creatives."),
        OperationSpec("update", "POST", "/adAccounts/{ad_account_id}/creatives/{creative_urn}", ACCOUNT_CREATIVES, BASE_WRITE, "implemented", WRITE, "Update one account-scoped creative. The docs sample path is partially truncated; this path is inferred."),
        OperationSpec("batch-update", "POST", "/adAccounts/{ad_account_id}/creatives?ids=List(...)", ACCOUNT_CREATIVES, BASE_WRITE, "implemented", RISKY, "Batch update account-scoped creatives."),
        OperationSpec("delete", "DELETE", "/adAccounts/{ad_account_id}/creatives/{creative_urn}", ACCOUNT_CREATIVES, BASE_WRITE, "implemented", RISKY, "Delete one account-scoped creative. The docs sample path is partially truncated; this path is inferred."),
        OperationSpec("batch-delete", "DELETE", "/adAccounts/{ad_account_id}/creatives?ids=List(...)", ACCOUNT_CREATIVES, BASE_WRITE, "implemented", RISKY, "Batch delete account-scoped creatives."),
    ),
    "third-party-tracking-tags": (
        OperationSpec("create", "POST", "/thirdPartyTrackingTags", THIRD_PARTY_TRACKING, BASE_WRITE, "implemented", WRITE, "Create one third-party tracking tag."),
        OperationSpec("get", "GET", "/thirdPartyTrackingTags/{tag_id}", THIRD_PARTY_TRACKING, BASE_READ, "implemented", READ, "Get one third-party tracking tag."),
        OperationSpec("list-by-creative", "GET", "/thirdPartyTrackingTags?q=creative", THIRD_PARTY_TRACKING, BASE_READ, "implemented", READ, "List third-party tracking tags for one creative."),
        OperationSpec("delete", "DELETE", "/thirdPartyTrackingTags/{tag_id}", THIRD_PARTY_TRACKING, BASE_WRITE, "implemented", RISKY, "Delete one third-party tracking tag."),
    ),
}


ALL_OPERATION_SPECS: Final[tuple[OperationSpec, ...]] = tuple(
    operation
    for family_operations in OPERATIONS_BY_FAMILY.values()
    for operation in family_operations
)
