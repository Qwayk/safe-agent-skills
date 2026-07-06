# OpenAI Ads API coverage

Last updated: **2026-07-06**

This file is the source coverage ledger for the OpenAI Ads safe API tool. The generated inventory comes from the official OpenAI Ads OpenAPI spec pinned at `docs/specs/openai-ads-openapi.json`. Manual rows cover official measurement and setup docs outside the spec.

## Boundary

- Official OpenAPI source: `https://developers.openai.com/ads/openapi.json`
- Server: `https://api.ads.openai.com/v1`
- OpenAPI: `3.1.0`
- Spec version: `2.3.0`
- Spec SHA-256: `a45e81ff54294cc570543d48ce71330cae2304e9cb9eda85d894e177df8b9d3b`
- Paths: **33**
- Operations: **41**
- Build strategy: **generated-inventory possible**, with manual rows for official measurement docs outside the OpenAPI spec.

## Safety labels

- `Direct read`: safe read command; still redacts secrets and private measurement values.
- `Review-first write`: dry-run plan first, then `--apply --yes --plan-in ...` for live apply.
- `High-risk write`: also needs `--ack-irreversible` when the operation can affect spend, serving, uploads, audiences, account state, auth, or measurement.
- `No snapshot`: live apply also needs `--ack-no-snapshot` when the API cannot reliably save before-state.

## Official OpenAPI operations

| Family | Operation | Method | Path | CLI command | Safety | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ad-account` | `ActivateAdAccountMethod` | `POST` | `/ad_account/activate` | `openai-ads-safe-agent-cli api ad-account activate-ad-account` | Review-first write: high-risk acknowledgement | Implemented |
| `ad-account` | `GetAdAccountMethod` | `GET` | `/ad_account` | `openai-ads-safe-agent-cli api ad-account get-ad-account` | Direct read | Implemented |
| `ad-account` | `PauseAdAccountMethod` | `POST` | `/ad_account/pause` | `openai-ads-safe-agent-cli api ad-account pause-ad-account` | Review-first write: high-risk acknowledgement | Implemented |
| `ad-account` | `UpdateAdAccountMethod` | `POST` | `/ad_account/brand` | `openai-ads-safe-agent-cli api ad-account update-ad-account` | Review-first write: high-risk acknowledgement | Implemented |
| `ad-groups` | `ActivateAdGroupMethod` | `POST` | `/ad_groups/{ad_group_id}/activate` | `openai-ads-safe-agent-cli api ad-groups activate-ad-group` | Review-first write: high-risk acknowledgement | Implemented |
| `ad-groups` | `ArchiveAdGroupMethod` | `POST` | `/ad_groups/{ad_group_id}/archive` | `openai-ads-safe-agent-cli api ad-groups archive-ad-group` | Review-first write: high-risk acknowledgement | Implemented |
| `ad-groups` | `CreateAdGroupMethod` | `POST` | `/ad_groups` | `openai-ads-safe-agent-cli api ad-groups create-ad-group` | Review-first write: no-snapshot acknowledgement | Implemented |
| `ad-groups` | `GetAdGroupMethod` | `GET` | `/ad_groups/{ad_group_id}` | `openai-ads-safe-agent-cli api ad-groups get-ad-group` | Direct read | Implemented |
| `ad-groups` | `ListAdGroupsMethod` | `GET` | `/ad_groups` | `openai-ads-safe-agent-cli api ad-groups list-ad-groups` | Direct read | Implemented |
| `ad-groups` | `PauseAdGroupMethod` | `POST` | `/ad_groups/{ad_group_id}/pause` | `openai-ads-safe-agent-cli api ad-groups pause-ad-group` | Review-first write: high-risk acknowledgement | Implemented |
| `ad-groups` | `UpdateAdGroupMethod` | `POST` | `/ad_groups/{ad_group_id}` | `openai-ads-safe-agent-cli api ad-groups update-ad-group` | Review-first write | Implemented |
| `ads` | `ActivateAdMethod` | `POST` | `/ads/{ad_id}/activate` | `openai-ads-safe-agent-cli api ads activate-ad` | Review-first write: high-risk acknowledgement | Implemented |
| `ads` | `ArchiveAdMethod` | `POST` | `/ads/{ad_id}/archive` | `openai-ads-safe-agent-cli api ads archive-ad` | Review-first write: high-risk acknowledgement | Implemented |
| `ads` | `CreateAdMethod` | `POST` | `/ads` | `openai-ads-safe-agent-cli api ads create-ad` | Review-first write: no-snapshot acknowledgement | Implemented |
| `ads` | `GetAdMethod` | `GET` | `/ads/{ad_id}` | `openai-ads-safe-agent-cli api ads get-ad` | Direct read | Implemented |
| `ads` | `ListAdsMethod` | `GET` | `/ads` | `openai-ads-safe-agent-cli api ads list-ads` | Direct read | Implemented |
| `ads` | `PauseAdMethod` | `POST` | `/ads/{ad_id}/pause` | `openai-ads-safe-agent-cli api ads pause-ad` | Review-first write: high-risk acknowledgement | Implemented |
| `ads` | `UpdateAdMethod` | `POST` | `/ads/{ad_id}` | `openai-ads-safe-agent-cli api ads update-ad` | Review-first write | Implemented |
| `campaigns` | `ActivateCampaignMethod` | `POST` | `/campaigns/{campaign_id}/activate` | `openai-ads-safe-agent-cli api campaigns activate-campaign` | Review-first write: high-risk acknowledgement | Implemented |
| `campaigns` | `ArchiveCampaignMethod` | `POST` | `/campaigns/{campaign_id}/archive` | `openai-ads-safe-agent-cli api campaigns archive-campaign` | Review-first write: high-risk acknowledgement | Implemented |
| `campaigns` | `CreateCampaignMethod` | `POST` | `/campaigns` | `openai-ads-safe-agent-cli api campaigns create-campaign` | Review-first write: no-snapshot acknowledgement | Implemented |
| `campaigns` | `GetCampaignMethod` | `GET` | `/campaigns/{campaign_id}` | `openai-ads-safe-agent-cli api campaigns get-campaign` | Direct read | Implemented |
| `campaigns` | `ListCampaignsMethod` | `GET` | `/campaigns` | `openai-ads-safe-agent-cli api campaigns list-campaigns` | Direct read | Implemented |
| `campaigns` | `PauseCampaignMethod` | `POST` | `/campaigns/{campaign_id}/pause` | `openai-ads-safe-agent-cli api campaigns pause-campaign` | Review-first write: high-risk acknowledgement | Implemented |
| `campaigns` | `UpdateCampaignMethod` | `POST` | `/campaigns/{campaign_id}` | `openai-ads-safe-agent-cli api campaigns update-campaign` | Review-first write | Implemented |
| `conversions` | `CreateConversionApiKeyMethod` | `POST` | `/conversions/api_keys` | `openai-ads-safe-agent-cli api conversions create-conversion-api-key` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `conversions` | `CreateConversionEventSettingMethod` | `POST` | `/conversions/event_settings` | `openai-ads-safe-agent-cli api conversions create-conversion-event-setting` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `conversions` | `CreateConversionSourceMethod` | `POST` | `/conversions/pixels` | `openai-ads-safe-agent-cli api conversions create-conversion-source` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `conversions` | `ListConversionEventSettingsMethod` | `GET` | `/conversions/event_settings` | `openai-ads-safe-agent-cli api conversions list-conversion-event-settings` | Direct read | Implemented |
| `conversions` | `PostConversionInsightsMethod` | `POST` | `/conversions/insights` | `openai-ads-safe-agent-cli api conversions post-conversion-insights` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `custom-audiences` | `ArchiveCustomAudienceMethod` | `POST` | `/custom_audiences/{custom_audience_id}/archive` | `openai-ads-safe-agent-cli api custom-audiences archive-custom-audience` | Review-first write: high-risk acknowledgement | Implemented |
| `custom-audiences` | `CreateCustomAudienceMethod` | `POST` | `/custom_audiences` | `openai-ads-safe-agent-cli api custom-audiences create-custom-audience` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `custom-audiences` | `CreateCustomAudienceUploadMethod` | `POST` | `/custom_audiences/upload` | `openai-ads-safe-agent-cli api custom-audiences create-custom-audience-upload` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `custom-audiences` | `GetCustomAudienceMethod` | `GET` | `/custom_audiences/{custom_audience_id}` | `openai-ads-safe-agent-cli api custom-audiences get-custom-audience` | Direct read | Implemented |
| `custom-audiences` | `ListCustomAudiencesMethod` | `GET` | `/custom_audiences` | `openai-ads-safe-agent-cli api custom-audiences list-custom-audiences` | Direct read | Implemented |
| `files` | `UploadImageMethod` | `POST` | `/upload` | `openai-ads-safe-agent-cli api files upload-image` | Review-first write: high-risk acknowledgement, no-snapshot acknowledgement | Implemented |
| `insights` | `GetAdAccountInsightsMethod` | `GET` | `/ad_account/insights` | `openai-ads-safe-agent-cli api insights get-ad-account-insights` | Direct read | Implemented |
| `insights` | `GetAdGroupInsightsMethod` | `GET` | `/ad_groups/{ad_group_id}/insights` | `openai-ads-safe-agent-cli api insights get-ad-group-insights` | Direct read | Implemented |
| `insights` | `GetAdInsightsMethod` | `GET` | `/ads/{ad_id}/insights` | `openai-ads-safe-agent-cli api insights get-ad-insights` | Direct read | Implemented |
| `insights` | `GetCampaignInsightsMethod` | `GET` | `/campaigns/{campaign_id}/insights` | `openai-ads-safe-agent-cli api insights get-campaign-insights` | Direct read | Implemented |
| `targeting` | `GetGeoLookupMethod` | `GET` | `/geo_lookup/search` | `openai-ads-safe-agent-cli api targeting get-geo-lookup` | Direct read | Implemented |

## Manual official-doc surfaces

| Surface | CLI command | Source | Safety | Status |
| --- | --- | --- | --- | --- |
| `JavaScript Pixel setup guidance` | `openai-ads-safe-agent-cli measurement pixel-guide` | https://developers.openai.com/ads/measurement-pixel | Local guidance/read | implemented-local-guidance |
| `Image tag or noscript fallback builder with redacted Pixel ID` | `openai-ads-safe-agent-cli measurement image-tag-build` | https://developers.openai.com/ads/image-tag | Local guidance/read | implemented-local-guidance |
| `Supported conversion event names and data types` | `openai-ads-safe-agent-cli measurement events-list` | https://developers.openai.com/ads/supported-events | Local guidance/read | implemented-local-guidance |
| `Server-side Conversions API event send to https://bzr.openai.com/v1/events` | `openai-ads-safe-agent-cli measurement conversions-send` | https://developers.openai.com/ads/conversions-api | Review-first measurement write; defaults to validate-only and requires apply approval for sends | implemented-review-first-write |
| `Product-feed workflow guidance; public API uses campaigns/ad groups/ads/insights, feed connection and catalog upload stay in Ads Manager/SFTP` | `openai-ads-safe-agent-cli product-feeds guide` | https://developers.openai.com/ads/product-feeds | Local guidance/read | implemented-local-guidance |
| `Campaign targeting guidance; live location lookup is covered by geo_lookup/search` | `openai-ads-safe-agent-cli targeting guide` | https://developers.openai.com/ads/campaign-targeting | Local guidance/read | implemented-local-guidance |

## Exclusions and access gates

- Ads Manager Beta access, account verification, billing, and API-key issuance are outside this CLI and must be handled in OpenAI Ads Manager.
- Product-feed connection and catalog upload are handled in Ads Manager/SFTP. The public Advertiser API commands cover product-feed campaigns, product sets, product-ad templates, and product-segmented insights.
- No generic raw-request command is included. Every covered operation has an explicit command generated from the official boundary or a named local measurement guide command.
