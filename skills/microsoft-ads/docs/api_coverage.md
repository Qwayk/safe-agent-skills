# API coverage (operations → CLI)

Purpose:
- Make “100% operation coverage” measurable and reviewable.
- Provide a deterministic mapping: every operation has exactly one CLI command.

## Summary

- Provider: Microsoft Advertising API (Microsoft Ads) v13
- Coverage definition: all operations for in-scope services (campaign-management, bulk, reporting, ad-insight, customer-management) discovered in official v13 WSDLs (see inventories below)
- Last audited (UTC): 2026-03-04

Canonical inventories (committed):
- `docs/official_operations_v13_2026-03-04.txt`
- `docs/official_wsdl_v13_2026-03-04/`
- `docs/wsdl_reconciliation_v13_2026-03-04.md`

Command naming rule (deterministic):
- `msads-api-tool <service> <operation-kebab>`

Safety gates:
- No network without `--live`
- Writes require `--apply` (and may require `--yes` / `--ack-irreversible` / `--plan-in` depending on risk), then currently require explicit no-snapshot approval before SOAP HTTP until before-state capture support exists

## Operation coverage (WSDL inventory)

### ad-insight (34 operations)

| Operation | CLI command |
|---|---|
| `GetBidOpportunities` | `msads-api-tool ad-insight get-bid-opportunities` |
| `GetBudgetOpportunities` | `msads-api-tool ad-insight get-budget-opportunities` |
| `GetKeywordOpportunities` | `msads-api-tool ad-insight get-keyword-opportunities` |
| `GetEstimatedBidByKeywordIds` | `msads-api-tool ad-insight get-estimated-bid-by-keyword-ids` |
| `GetEstimatedPositionByKeywordIds` | `msads-api-tool ad-insight get-estimated-position-by-keyword-ids` |
| `GetEstimatedBidByKeywords` | `msads-api-tool ad-insight get-estimated-bid-by-keywords` |
| `GetEstimatedPositionByKeywords` | `msads-api-tool ad-insight get-estimated-position-by-keywords` |
| `GetBidLandscapeByAdGroupIds` | `msads-api-tool ad-insight get-bid-landscape-by-ad-group-ids` |
| `GetBidLandscapeByCampaignIds` | `msads-api-tool ad-insight get-bid-landscape-by-campaign-ids` |
| `GetBidLandscapeByKeywordIds` | `msads-api-tool ad-insight get-bid-landscape-by-keyword-ids` |
| `GetHistoricalKeywordPerformance` | `msads-api-tool ad-insight get-historical-keyword-performance` |
| `GetHistoricalSearchCount` | `msads-api-tool ad-insight get-historical-search-count` |
| `GetKeywordCategories` | `msads-api-tool ad-insight get-keyword-categories` |
| `GetKeywordDemographics` | `msads-api-tool ad-insight get-keyword-demographics` |
| `GetKeywordLocations` | `msads-api-tool ad-insight get-keyword-locations` |
| `SuggestKeywordsForUrl` | `msads-api-tool ad-insight suggest-keywords-for-url` |
| `SuggestKeywordsFromExistingKeywords` | `msads-api-tool ad-insight suggest-keywords-from-existing-keywords` |
| `GetAuctionInsightData` | `msads-api-tool ad-insight get-auction-insight-data` |
| `GetDomainCategories` | `msads-api-tool ad-insight get-domain-categories` |
| `PutMetricData` | `msads-api-tool ad-insight put-metric-data` |
| `GetKeywordIdeaCategories` | `msads-api-tool ad-insight get-keyword-idea-categories` |
| `GetKeywordIdeas` | `msads-api-tool ad-insight get-keyword-ideas` |
| `GetKeywordTrafficEstimates` | `msads-api-tool ad-insight get-keyword-traffic-estimates` |
| `GetAutoApplyOptInStatus` | `msads-api-tool ad-insight get-auto-apply-opt-in-status` |
| `SetAutoApplyOptInStatus` | `msads-api-tool ad-insight set-auto-apply-opt-in-status` |
| `GetPerformanceInsightsDetailDataByAccountId` | `msads-api-tool ad-insight get-performance-insights-detail-data-by-account-id` |
| `GetRecommendations` | `msads-api-tool ad-insight get-recommendations` |
| `TagRecommendations` | `msads-api-tool ad-insight tag-recommendations` |
| `GetTextAssetSuggestionsByFinalUrls` | `msads-api-tool ad-insight get-text-asset-suggestions-by-final-urls` |
| `ApplyRecommendations` | `msads-api-tool ad-insight apply-recommendations` |
| `DismissRecommendations` | `msads-api-tool ad-insight dismiss-recommendations` |
| `RetrieveRecommendations` | `msads-api-tool ad-insight retrieve-recommendations` |
| `GetAudienceFullEstimation` | `msads-api-tool ad-insight get-audience-full-estimation` |
| `GetAudienceBreakdown` | `msads-api-tool ad-insight get-audience-breakdown` |

### bulk (6 operations)

| Operation | CLI command |
|---|---|
| `DownloadCampaignsByAccountIds` | `msads-api-tool bulk download-campaigns-by-account-ids` |
| `DownloadCampaignsByCampaignIds` | `msads-api-tool bulk download-campaigns-by-campaign-ids` |
| `GetBulkDownloadStatus` | `msads-api-tool bulk get-bulk-download-status` |
| `GetBulkUploadUrl` | `msads-api-tool bulk get-bulk-upload-url` |
| `GetBulkUploadStatus` | `msads-api-tool bulk get-bulk-upload-status` |
| `UploadEntityRecords` | `msads-api-tool bulk upload-entity-records` |

### campaign-management (190 operations)

| Operation | CLI command |
|---|---|
| `AddCampaigns` | `msads-api-tool campaign-management add-campaigns` |
| `GetCampaignsByAccountId` | `msads-api-tool campaign-management get-campaigns-by-account-id` |
| `GetCampaignsByIds` | `msads-api-tool campaign-management get-campaigns-by-ids` |
| `DeleteCampaigns` | `msads-api-tool campaign-management delete-campaigns` |
| `UpdateCampaigns` | `msads-api-tool campaign-management update-campaigns` |
| `GetNegativeSitesByCampaignIds` | `msads-api-tool campaign-management get-negative-sites-by-campaign-ids` |
| `SetNegativeSitesToCampaigns` | `msads-api-tool campaign-management set-negative-sites-to-campaigns` |
| `GetConfigValue` | `msads-api-tool campaign-management get-config-value` |
| `GetBSCCountries` | `msads-api-tool campaign-management get-bsc-countries` |
| `AddAdGroups` | `msads-api-tool campaign-management add-ad-groups` |
| `DeleteAdGroups` | `msads-api-tool campaign-management delete-ad-groups` |
| `GetAdGroupsByIds` | `msads-api-tool campaign-management get-ad-groups-by-ids` |
| `GetAdGroupsByCampaignId` | `msads-api-tool campaign-management get-ad-groups-by-campaign-id` |
| `UpdateAdGroups` | `msads-api-tool campaign-management update-ad-groups` |
| `GetNegativeSitesByAdGroupIds` | `msads-api-tool campaign-management get-negative-sites-by-ad-group-ids` |
| `SetNegativeSitesToAdGroups` | `msads-api-tool campaign-management set-negative-sites-to-ad-groups` |
| `GetGeoLocationsFileUrl` | `msads-api-tool campaign-management get-geo-locations-file-url` |
| `AddAds` | `msads-api-tool campaign-management add-ads` |
| `DeleteAds` | `msads-api-tool campaign-management delete-ads` |
| `GetAdsByEditorialStatus` | `msads-api-tool campaign-management get-ads-by-editorial-status` |
| `GetAdsByIds` | `msads-api-tool campaign-management get-ads-by-ids` |
| `GetAdsByAdGroupId` | `msads-api-tool campaign-management get-ads-by-ad-group-id` |
| `UpdateAds` | `msads-api-tool campaign-management update-ads` |
| `AddKeywords` | `msads-api-tool campaign-management add-keywords` |
| `DeleteKeywords` | `msads-api-tool campaign-management delete-keywords` |
| `GetKeywordsByEditorialStatus` | `msads-api-tool campaign-management get-keywords-by-editorial-status` |
| `GetKeywordsByIds` | `msads-api-tool campaign-management get-keywords-by-ids` |
| `GetKeywordsByAdGroupId` | `msads-api-tool campaign-management get-keywords-by-ad-group-id` |
| `UpdateKeywords` | `msads-api-tool campaign-management update-keywords` |
| `AppealEditorialRejections` | `msads-api-tool campaign-management appeal-editorial-rejections` |
| `GetEditorialReasonsByIds` | `msads-api-tool campaign-management get-editorial-reasons-by-ids` |
| `GetAccountMigrationStatuses` | `msads-api-tool campaign-management get-account-migration-statuses` |
| `SetAccountProperties` | `msads-api-tool campaign-management set-account-properties` |
| `GetAccountProperties` | `msads-api-tool campaign-management get-account-properties` |
| `AddAdExtensions` | `msads-api-tool campaign-management add-ad-extensions` |
| `GetAdExtensionsByIds` | `msads-api-tool campaign-management get-ad-extensions-by-ids` |
| `UpdateAdExtensions` | `msads-api-tool campaign-management update-ad-extensions` |
| `DeleteAdExtensions` | `msads-api-tool campaign-management delete-ad-extensions` |
| `GetAdExtensionsEditorialReasons` | `msads-api-tool campaign-management get-ad-extensions-editorial-reasons` |
| `SetAdExtensionsAssociations` | `msads-api-tool campaign-management set-ad-extensions-associations` |
| `GetAdExtensionsAssociations` | `msads-api-tool campaign-management get-ad-extensions-associations` |
| `DeleteAdExtensionsAssociations` | `msads-api-tool campaign-management delete-ad-extensions-associations` |
| `GetAdExtensionIdsByAccountId` | `msads-api-tool campaign-management get-ad-extension-ids-by-account-id` |
| `AddMedia` | `msads-api-tool campaign-management add-media` |
| `DeleteMedia` | `msads-api-tool campaign-management delete-media` |
| `GetMediaMetaDataByAccountId` | `msads-api-tool campaign-management get-media-meta-data-by-account-id` |
| `GetMediaMetaDataByIds` | `msads-api-tool campaign-management get-media-meta-data-by-ids` |
| `GetMediaAssociations` | `msads-api-tool campaign-management get-media-associations` |
| `GetAdGroupCriterionsByIds` | `msads-api-tool campaign-management get-ad-group-criterions-by-ids` |
| `AddAdGroupCriterions` | `msads-api-tool campaign-management add-ad-group-criterions` |
| `UpdateAdGroupCriterions` | `msads-api-tool campaign-management update-ad-group-criterions` |
| `DeleteAdGroupCriterions` | `msads-api-tool campaign-management delete-ad-group-criterions` |
| `ApplyProductPartitionActions` | `msads-api-tool campaign-management apply-product-partition-actions` |
| `ApplyHotelGroupActions` | `msads-api-tool campaign-management apply-hotel-group-actions` |
| `ApplyAssetGroupListingGroupActions` | `msads-api-tool campaign-management apply-asset-group-listing-group-actions` |
| `GetAssetGroupListingGroupsByIds` | `msads-api-tool campaign-management get-asset-group-listing-groups-by-ids` |
| `GetBMCStoresByCustomerId` | `msads-api-tool campaign-management get-bmc-stores-by-customer-id` |
| `AddNegativeKeywordsToEntities` | `msads-api-tool campaign-management add-negative-keywords-to-entities` |
| `GetNegativeKeywordsByEntityIds` | `msads-api-tool campaign-management get-negative-keywords-by-entity-ids` |
| `DeleteNegativeKeywordsFromEntities` | `msads-api-tool campaign-management delete-negative-keywords-from-entities` |
| `GetSharedEntitiesByAccountId` | `msads-api-tool campaign-management get-shared-entities-by-account-id` |
| `GetSharedEntities` | `msads-api-tool campaign-management get-shared-entities` |
| `AddSharedEntity` | `msads-api-tool campaign-management add-shared-entity` |
| `GetListItemsBySharedList` | `msads-api-tool campaign-management get-list-items-by-shared-list` |
| `AddListItemsToSharedList` | `msads-api-tool campaign-management add-list-items-to-shared-list` |
| `UpdateSharedEntities` | `msads-api-tool campaign-management update-shared-entities` |
| `DeleteListItemsFromSharedList` | `msads-api-tool campaign-management delete-list-items-from-shared-list` |
| `SetSharedEntityAssociations` | `msads-api-tool campaign-management set-shared-entity-associations` |
| `DeleteSharedEntityAssociations` | `msads-api-tool campaign-management delete-shared-entity-associations` |
| `GetSharedEntityAssociationsBySharedEntityIds` | `msads-api-tool campaign-management get-shared-entity-associations-by-shared-entity-ids` |
| `GetSharedEntityAssociationsByEntityIds` | `msads-api-tool campaign-management get-shared-entity-associations-by-entity-ids` |
| `DeleteSharedEntities` | `msads-api-tool campaign-management delete-shared-entities` |
| `GetCampaignSizesByAccountId` | `msads-api-tool campaign-management get-campaign-sizes-by-account-id` |
| `AddCampaignCriterions` | `msads-api-tool campaign-management add-campaign-criterions` |
| `UpdateCampaignCriterions` | `msads-api-tool campaign-management update-campaign-criterions` |
| `DeleteCampaignCriterions` | `msads-api-tool campaign-management delete-campaign-criterions` |
| `GetCampaignCriterionsByIds` | `msads-api-tool campaign-management get-campaign-criterions-by-ids` |
| `AddBudgets` | `msads-api-tool campaign-management add-budgets` |
| `UpdateBudgets` | `msads-api-tool campaign-management update-budgets` |
| `DeleteBudgets` | `msads-api-tool campaign-management delete-budgets` |
| `GetBudgetsByIds` | `msads-api-tool campaign-management get-budgets-by-ids` |
| `GetCampaignIdsByBudgetIds` | `msads-api-tool campaign-management get-campaign-ids-by-budget-ids` |
| `AddBidStrategies` | `msads-api-tool campaign-management add-bid-strategies` |
| `UpdateBidStrategies` | `msads-api-tool campaign-management update-bid-strategies` |
| `DeleteBidStrategies` | `msads-api-tool campaign-management delete-bid-strategies` |
| `GetBidStrategiesByIds` | `msads-api-tool campaign-management get-bid-strategies-by-ids` |
| `GetCampaignIdsByBidStrategyIds` | `msads-api-tool campaign-management get-campaign-ids-by-bid-strategy-ids` |
| `AddAudienceGroups` | `msads-api-tool campaign-management add-audience-groups` |
| `UpdateAudienceGroups` | `msads-api-tool campaign-management update-audience-groups` |
| `DeleteAudienceGroups` | `msads-api-tool campaign-management delete-audience-groups` |
| `GetAudienceGroupsByIds` | `msads-api-tool campaign-management get-audience-groups-by-ids` |
| `AddAssetGroups` | `msads-api-tool campaign-management add-asset-groups` |
| `UpdateAssetGroups` | `msads-api-tool campaign-management update-asset-groups` |
| `DeleteAssetGroups` | `msads-api-tool campaign-management delete-asset-groups` |
| `GetAssetGroupsByIds` | `msads-api-tool campaign-management get-asset-groups-by-ids` |
| `GetAssetGroupsByCampaignId` | `msads-api-tool campaign-management get-asset-groups-by-campaign-id` |
| `GetAssetGroupsEditorialReasons` | `msads-api-tool campaign-management get-asset-groups-editorial-reasons` |
| `SetAudienceGroupAssetGroupAssociations` | `msads-api-tool campaign-management set-audience-group-asset-group-associations` |
| `DeleteAudienceGroupAssetGroupAssociations` | `msads-api-tool campaign-management delete-audience-group-asset-group-associations` |
| `GetAudienceGroupAssetGroupAssociationsByAssetGroupIds` | `msads-api-tool campaign-management get-audience-group-asset-group-associations-by-asset-group-ids` |
| `GetAudienceGroupAssetGroupAssociationsByAudienceGroupIds` | `msads-api-tool campaign-management get-audience-group-asset-group-associations-by-audience-group-ids` |
| `AddAudiences` | `msads-api-tool campaign-management add-audiences` |
| `UpdateAudiences` | `msads-api-tool campaign-management update-audiences` |
| `DeleteAudiences` | `msads-api-tool campaign-management delete-audiences` |
| `GetAudiencesByIds` | `msads-api-tool campaign-management get-audiences-by-ids` |
| `ApplyCustomerListItems` | `msads-api-tool campaign-management apply-customer-list-items` |
| `ApplyCustomerListUserData` | `msads-api-tool campaign-management apply-customer-list-user-data` |
| `GetUetTagsByIds` | `msads-api-tool campaign-management get-uet-tags-by-ids` |
| `AddUetTags` | `msads-api-tool campaign-management add-uet-tags` |
| `UpdateUetTags` | `msads-api-tool campaign-management update-uet-tags` |
| `GetConversionGoalsByIds` | `msads-api-tool campaign-management get-conversion-goals-by-ids` |
| `GetConversionGoalsByTagIds` | `msads-api-tool campaign-management get-conversion-goals-by-tag-ids` |
| `AddConversionGoals` | `msads-api-tool campaign-management add-conversion-goals` |
| `UpdateConversionGoals` | `msads-api-tool campaign-management update-conversion-goals` |
| `ApplyOfflineConversions` | `msads-api-tool campaign-management apply-offline-conversions` |
| `ApplyOfflineConversionAdjustments` | `msads-api-tool campaign-management apply-offline-conversion-adjustments` |
| `ApplyOnlineConversionAdjustments` | `msads-api-tool campaign-management apply-online-conversion-adjustments` |
| `GetOfflineConversionReports` | `msads-api-tool campaign-management get-offline-conversion-reports` |
| `GetOfflineConversionReportByGoalIds` | `msads-api-tool campaign-management get-offline-conversion-report-by-goal-ids` |
| `AddLabels` | `msads-api-tool campaign-management add-labels` |
| `DeleteLabels` | `msads-api-tool campaign-management delete-labels` |
| `UpdateLabels` | `msads-api-tool campaign-management update-labels` |
| `GetLabelsByIds` | `msads-api-tool campaign-management get-labels-by-ids` |
| `SetLabelAssociations` | `msads-api-tool campaign-management set-label-associations` |
| `DeleteLabelAssociations` | `msads-api-tool campaign-management delete-label-associations` |
| `GetLabelAssociationsByEntityIds` | `msads-api-tool campaign-management get-label-associations-by-entity-ids` |
| `GetLabelAssociationsByLabelIds` | `msads-api-tool campaign-management get-label-associations-by-label-ids` |
| `AddExperiments` | `msads-api-tool campaign-management add-experiments` |
| `DeleteExperiments` | `msads-api-tool campaign-management delete-experiments` |
| `UpdateExperiments` | `msads-api-tool campaign-management update-experiments` |
| `GetExperimentsByIds` | `msads-api-tool campaign-management get-experiments-by-ids` |
| `GetProfileDataFileUrl` | `msads-api-tool campaign-management get-profile-data-file-url` |
| `SearchCompanies` | `msads-api-tool campaign-management search-companies` |
| `GetFileImportUploadUrl` | `msads-api-tool campaign-management get-file-import-upload-url` |
| `AddImportJobs` | `msads-api-tool campaign-management add-import-jobs` |
| `GetImportResults` | `msads-api-tool campaign-management get-import-results` |
| `GetImportJobsByIds` | `msads-api-tool campaign-management get-import-jobs-by-ids` |
| `DeleteImportJobs` | `msads-api-tool campaign-management delete-import-jobs` |
| `GetImportEntityIdsMapping` | `msads-api-tool campaign-management get-import-entity-ids-mapping` |
| `UpdateImportJobs` | `msads-api-tool campaign-management update-import-jobs` |
| `AddVideos` | `msads-api-tool campaign-management add-videos` |
| `DeleteVideos` | `msads-api-tool campaign-management delete-videos` |
| `GetVideosByIds` | `msads-api-tool campaign-management get-videos-by-ids` |
| `UpdateVideos` | `msads-api-tool campaign-management update-videos` |
| `AddHTML5s` | `msads-api-tool campaign-management add-html5s` |
| `GetHTML5sByIds` | `msads-api-tool campaign-management get-html5s-by-ids` |
| `DeleteHTML5s` | `msads-api-tool campaign-management delete-html5s` |
| `AddCampaignConversionGoals` | `msads-api-tool campaign-management add-campaign-conversion-goals` |
| `DeleteCampaignConversionGoals` | `msads-api-tool campaign-management delete-campaign-conversion-goals` |
| `AddDataExclusions` | `msads-api-tool campaign-management add-data-exclusions` |
| `UpdateDataExclusions` | `msads-api-tool campaign-management update-data-exclusions` |
| `DeleteDataExclusions` | `msads-api-tool campaign-management delete-data-exclusions` |
| `GetDataExclusionsByIds` | `msads-api-tool campaign-management get-data-exclusions-by-ids` |
| `GetDataExclusionsByAccountId` | `msads-api-tool campaign-management get-data-exclusions-by-account-id` |
| `AddSeasonalityAdjustments` | `msads-api-tool campaign-management add-seasonality-adjustments` |
| `UpdateSeasonalityAdjustments` | `msads-api-tool campaign-management update-seasonality-adjustments` |
| `DeleteSeasonalityAdjustments` | `msads-api-tool campaign-management delete-seasonality-adjustments` |
| `GetSeasonalityAdjustmentsByIds` | `msads-api-tool campaign-management get-seasonality-adjustments-by-ids` |
| `GetSeasonalityAdjustmentsByAccountId` | `msads-api-tool campaign-management get-seasonality-adjustments-by-account-id` |
| `CreateAssetGroupRecommendation` | `msads-api-tool campaign-management create-asset-group-recommendation` |
| `CreateResponsiveAdRecommendation` | `msads-api-tool campaign-management create-responsive-ad-recommendation` |
| `CreateResponsiveSearchAdRecommendation` | `msads-api-tool campaign-management create-responsive-search-ad-recommendation` |
| `RefineAssetGroupRecommendation` | `msads-api-tool campaign-management refine-asset-group-recommendation` |
| `RefineResponsiveAdRecommendation` | `msads-api-tool campaign-management refine-responsive-ad-recommendation` |
| `RefineResponsiveSearchAdRecommendation` | `msads-api-tool campaign-management refine-responsive-search-ad-recommendation` |
| `GetResponsiveAdRecommendationJob` | `msads-api-tool campaign-management get-responsive-ad-recommendation-job` |
| `UpdateConversionValueRules` | `msads-api-tool campaign-management update-conversion-value-rules` |
| `UpdateConversionValueRulesStatus` | `msads-api-tool campaign-management update-conversion-value-rules-status` |
| `AddConversionValueRules` | `msads-api-tool campaign-management add-conversion-value-rules` |
| `GetConversionValueRulesByAccountId` | `msads-api-tool campaign-management get-conversion-value-rules-by-account-id` |
| `GetConversionValueRulesByIds` | `msads-api-tool campaign-management get-conversion-value-rules-by-ids` |
| `AddBrandKits` | `msads-api-tool campaign-management add-brand-kits` |
| `UpdateBrandKits` | `msads-api-tool campaign-management update-brand-kits` |
| `DeleteBrandKits` | `msads-api-tool campaign-management delete-brand-kits` |
| `CreateBrandKitRecommendation` | `msads-api-tool campaign-management create-brand-kit-recommendation` |
| `AddNewCustomerAcquisitionGoals` | `msads-api-tool campaign-management add-new-customer-acquisition-goals` |
| `UpdateNewCustomerAcquisitionGoals` | `msads-api-tool campaign-management update-new-customer-acquisition-goals` |
| `GetNewCustomerAcquisitionGoalsByAccountId` | `msads-api-tool campaign-management get-new-customer-acquisition-goals-by-account-id` |
| `GetBrandKitsByAccountId` | `msads-api-tool campaign-management get-brand-kits-by-account-id` |
| `GetBrandKitsByIds` | `msads-api-tool campaign-management get-brand-kits-by-ids` |
| `GetClipchampTemplates` | `msads-api-tool campaign-management get-clipchamp-templates` |
| `GetSupportedClipchampAudio` | `msads-api-tool campaign-management get-supported-clipchamp-audio` |
| `GetSupportedFonts` | `msads-api-tool campaign-management get-supported-fonts` |
| `GetHealthCheck` | `msads-api-tool campaign-management get-health-check` |
| `GetDiagnostics` | `msads-api-tool campaign-management get-diagnostics` |
| `GetAnnotationOptOut` | `msads-api-tool campaign-management get-annotation-opt-out` |
| `UpdateAnnotationOptOut` | `msads-api-tool campaign-management update-annotation-opt-out` |
| `AddLinkedInSegments` | `msads-api-tool campaign-management add-linked-in-segments` |
| `DeleteLinkedInSegments` | `msads-api-tool campaign-management delete-linked-in-segments` |
| `UpdateLinkedInSegments` | `msads-api-tool campaign-management update-linked-in-segments` |

### customer-management (39 operations)

| Operation | CLI command |
|---|---|
| `GetAccountsInfo` | `msads-api-tool customer-management get-accounts-info` |
| `FindAccounts` | `msads-api-tool customer-management find-accounts` |
| `AddAccount` | `msads-api-tool customer-management add-account` |
| `UpdateAccount` | `msads-api-tool customer-management update-account` |
| `GetCustomer` | `msads-api-tool customer-management get-customer` |
| `UpdateCustomer` | `msads-api-tool customer-management update-customer` |
| `SignupCustomer` | `msads-api-tool customer-management signup-customer` |
| `GetAccount` | `msads-api-tool customer-management get-account` |
| `GetCustomersInfo` | `msads-api-tool customer-management get-customers-info` |
| `DeleteAccount` | `msads-api-tool customer-management delete-account` |
| `DeleteCustomer` | `msads-api-tool customer-management delete-customer` |
| `UpdateUser` | `msads-api-tool customer-management update-user` |
| `UpdateUserRoles` | `msads-api-tool customer-management update-user-roles` |
| `GetUser` | `msads-api-tool customer-management get-user` |
| `GetCurrentUser` | `msads-api-tool customer-management get-current-user` |
| `DeleteUser` | `msads-api-tool customer-management delete-user` |
| `GetUsersInfo` | `msads-api-tool customer-management get-users-info` |
| `GetCustomerPilotFeatures` | `msads-api-tool customer-management get-customer-pilot-features` |
| `GetAccountPilotFeatures` | `msads-api-tool customer-management get-account-pilot-features` |
| `GetPilotFeaturesCountries` | `msads-api-tool customer-management get-pilot-features-countries` |
| `GetAccessibleCustomer` | `msads-api-tool customer-management get-accessible-customer` |
| `FindAccountsOrCustomersInfo` | `msads-api-tool customer-management find-accounts-or-customers-info` |
| `UpgradeCustomerToAgency` | `msads-api-tool customer-management upgrade-customer-to-agency` |
| `AddPrepayAccount` | `msads-api-tool customer-management add-prepay-account` |
| `UpdatePrepayAccount` | `msads-api-tool customer-management update-prepay-account` |
| `MapCustomerIdToExternalCustomerId` | `msads-api-tool customer-management map-customer-id-to-external-customer-id` |
| `MapAccountIdToExternalAccountIds` | `msads-api-tool customer-management map-account-id-to-external-account-ids` |
| `SearchCustomers` | `msads-api-tool customer-management search-customers` |
| `AddClientLinks` | `msads-api-tool customer-management add-client-links` |
| `UpdateClientLinks` | `msads-api-tool customer-management update-client-links` |
| `SearchClientLinks` | `msads-api-tool customer-management search-client-links` |
| `SearchAccounts` | `msads-api-tool customer-management search-accounts` |
| `SendUserInvitation` | `msads-api-tool customer-management send-user-invitation` |
| `SearchUserInvitations` | `msads-api-tool customer-management search-user-invitations` |
| `ValidateAddress` | `msads-api-tool customer-management validate-address` |
| `GetLinkedAccountsAndCustomersInfo` | `msads-api-tool customer-management get-linked-accounts-and-customers-info` |
| `GetUserMFAStatus` | `msads-api-tool customer-management get-user-mfa-status` |
| `GetNotifications` | `msads-api-tool customer-management get-notifications` |
| `DismissNotifications` | `msads-api-tool customer-management dismiss-notifications` |

### reporting (2 operations)

| Operation | CLI command |
|---|---|
| `SubmitGenerateReport` | `msads-api-tool reporting submit-generate-report` |
| `PollGenerateReport` | `msads-api-tool reporting poll-generate-report` |
