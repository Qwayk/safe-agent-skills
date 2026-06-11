# API coverage

This file is the main reference for the Google Business Profile coverage claim in this tool.

## Current reality

- The official boundary for this tool is the full Google Business Profile API family:
  - newer specialized APIs first
  - Business Calls API
  - Media upload v1
  - remaining official Google My Business `v4.9` surface
- The foundation commands are implemented:
  - `onboarding`
  - `auth login`
  - `auth check`
  - `auth token set`
  - `auth token status`
  - `runs list`
  - `runs show`
- The exact machine-readable method inventory lives in `docs/official_inventory.json`.
- This tool currently includes `account-management` (read/write), `business-info` (read/write), `notifications` (read/write), and `media-upload-v1` (write) commands listed below.
- This tool currently includes `business-calls` (read/write), `lodging` (read/write), `place-actions` (read/write, metadata lookup), `performance` (read-only), and `legacy-v49` focused reviews/media follow-up commands listed below.
- This tool currently includes `verifications` commands listed below.

## Status labels

- `implemented`: shipped in the current CLI
- `planned`: approved for the command surface but not shipped yet
- `access-gated`: Google approval, role, or API enablement is required before live use
- `provider-discontinued`: Google has discontinued the surface
- `not-shipping`: kept in the ledger for honesty, but not currently a live command target
- `discovery-only`: appears in official discovery data but not in the normal REST overview
- `legacy-v49`: part of the remaining Google My Business `v4.9` surface
- `live-unverified`: not yet proved with live Google access in this repo

## Implemented foundation commands

| Area | Command | Status | Notes |
|---|---|---|---|
| Onboarding | `google-business-profile-safe-cli onboarding` | `implemented` | Creates local `.env` from `.env.example` and prints safe next steps |
| OAuth login | `google-business-profile-safe-cli auth login` | `implemented` | Installed-app flow; stores credentials in `.state/oauth_credentials.json` |
| Auth health | `google-business-profile-safe-cli auth check` | `implemented` | Validates stored credentials and refreshability |
| Token import | `google-business-profile-safe-cli auth token set --file token.json` | `implemented` | Manual credential import |
| Token status | `google-business-profile-safe-cli auth token status` | `implemented` | Never prints token values |
| Run history | `google-business-profile-safe-cli runs list` / `runs show` | `implemented` | Local run index only |
| Account management (read-only) | `google-business-profile-safe-cli account-management accounts list` | `implemented` | Read-only account-management commands |
| Account management (read-only) | `google-business-profile-safe-cli account-management accounts get` | `implemented` | Read-only account-management commands |
| Account management (read-only) | `google-business-profile-safe-cli account-management accounts admins list` | `implemented` | Read-only account-management commands |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts create` | `implemented` | Write-side account-management command |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts admins create` | `implemented` | Write-side account-management command; safe subset requires invitee email in `admin` and supports only `OWNER` or `MANAGER` |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts admins delete` | `implemented` | Write-side account-management command; exact admin resource delete with follow-up list verification |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts admins patch` | `implemented` | Write-side account-management command; safe subset updates only `role` and supports only `OWNER` or `MANAGER` |
| Account management (read/write) | `google-business-profile-safe-cli account-management locations admins create` | `implemented` | Write-side account-management command; safe subset supports `admin` or `account` identity and roles `OWNER`, `MANAGER`, `SITE_MANAGER` |
| Account management (read/write) | `google-business-profile-safe-cli account-management locations admins delete` | `implemented` | Write-side account-management command; exact admin resource delete with follow-up list verification |
| Account management (read/write) | `google-business-profile-safe-cli account-management locations admins patch` | `implemented` | Write-side account-management command; safe subset updates only `role` and supports `OWNER`, `MANAGER`, `SITE_MANAGER` |
| Account management (read/write) | `google-business-profile-safe-cli account-management locations transfer` | `implemented` | Write-side account-management command with verification against source and destination account location lists |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts invitations accept` | `implemented` | Account-access state change |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts invitations decline` | `implemented` | Account-access state change |
| Account management (read-only) | `google-business-profile-safe-cli account-management accounts invitations list` | `implemented` | Read-only account-management commands |
| Account management (read-only) | `google-business-profile-safe-cli account-management locations admins list` | `implemented` | Read-only account-management commands |
| Account management (read/write) | `google-business-profile-safe-cli account-management accounts patch` | `implemented` | Write-side account-management command |
| Business info (read-only) | `google-business-profile-safe-cli business-info accounts locations list` | `implemented` | Read-only business-info commands |
| Business info (write) | `google-business-profile-safe-cli business-info accounts locations create` | `implemented` | Write-side business-info command |
| Business info (read-only) | `google-business-profile-safe-cli business-info locations get` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info locations get-attributes` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info locations get-google-updated` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info locations attributes get-google-updated` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info attributes list` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info categories list` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info categories batch-get` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info chains search` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info chains get` | `implemented` | Read-only business-info commands |
| Business info (read-only) | `google-business-profile-safe-cli business-info google-locations search` | `implemented` | Read-only business-info commands |
| Business info (write) | `google-business-profile-safe-cli business-info locations patch` | `implemented` | Write-side business-info command |
| Business info (write) | `google-business-profile-safe-cli business-info locations update-attributes` | `implemented` | Write-side business-info command |
| Business info (write) | `google-business-profile-safe-cli business-info locations delete` | `implemented` | Write-side business-info command |
| Lodging (read-only) | `google-business-profile-safe-cli lodging locations get-lodging` | `implemented` | Read-only lodging command |
| Lodging (write) | `google-business-profile-safe-cli lodging locations update-lodging` | `implemented` | Write-side lodging command |
| Lodging (read-only) | `google-business-profile-safe-cli lodging locations lodging get-google-updated` | `implemented` | Read-only lodging command |
| Business Calls (read-only) | `google-business-profile-safe-cli business-calls locations get-business-calls-settings` | `implemented` | Read-only business-calls command |
| Business Calls (read/write) | `google-business-profile-safe-cli business-calls locations update-business-calls-settings` | `implemented` | Write-side business-calls command |
| Business Calls (read-only) | `google-business-profile-safe-cli business-calls locations business-calls-insights list` | `implemented` | Read-only business-calls command |
| Performance (read-only) | `google-business-profile-safe-cli performance locations fetch-multi-daily-metrics-time-series` | `implemented` | Read-only performance command |
| Performance (read-only) | `google-business-profile-safe-cli performance locations get-daily-metrics-time-series` | `implemented` | Read-only performance command |
| Performance (read-only) | `google-business-profile-safe-cli performance locations search-keywords impressions monthly list` | `implemented` | Read-only performance command |
| Notifications (read-only) | `google-business-profile-safe-cli notifications accounts get-notification-setting` | `implemented` | Read/write notifications family command |
| Notifications (write) | `google-business-profile-safe-cli notifications accounts update-notification-setting` | `implemented` | Write-side notifications family command |
| Media upload v1 (write) | `google-business-profile-safe-cli media-upload-v1 media upload` | `implemented` | One-method write slice with metadata and binary upload modes |
| Place Actions (read/write) | `google-business-profile-safe-cli place-actions locations place-action-links create` | `implemented` | Place-actions command family |
| Place Actions (write) | `google-business-profile-safe-cli place-actions locations place-action-links delete` | `implemented` | Place-actions command family |
| Place Actions (read-only) | `google-business-profile-safe-cli place-actions locations place-action-links get` | `implemented` | Place-actions command family |
| Place Actions (read-only) | `google-business-profile-safe-cli place-actions locations place-action-links list` | `implemented` | Place-actions command family |
| Place Actions (write) | `google-business-profile-safe-cli place-actions locations place-action-links patch` | `implemented` | Place-actions command family |
| Place Actions (read-only) | `google-business-profile-safe-cli place-actions place-action-type-metadata list` | `implemented` | Place-actions command family |
| Verifications (read-only) | `google-business-profile-safe-cli verifications locations fetch-verification-options` | `implemented` | Read-only verifications command |
| Verifications (read-only) | `google-business-profile-safe-cli verifications locations get-voice-of-merchant-state` | `implemented` | Read-only verifications command |
| Verifications (read-only) | `google-business-profile-safe-cli verifications locations verifications list` | `implemented` | Read-only verifications command |
| Verifications (write) | `google-business-profile-safe-cli verifications locations verify` | `implemented` | Write-side verifications command |
| Verifications (write) | `google-business-profile-safe-cli verifications locations verifications complete` | `implemented` | Write-side verifications command |
| Verifications (write) | `google-business-profile-safe-cli verifications verification-tokens generate` | `implemented` | Discovery-backed write command with response-derived output |
| Legacy v4.9 reviews (read-only) | `google-business-profile-safe-cli legacy-v49 accounts locations reviews list` | `implemented` | Legacy location review list with paging and official order-by validation |
| Legacy v4.9 reviews (read-only) | `google-business-profile-safe-cli legacy-v49 accounts locations reviews get` | `implemented` | Legacy single-review read command |
| Legacy v4.9 reviews (write) | `google-business-profile-safe-cli legacy-v49 accounts locations reviews update-reply` | `implemented` | Legacy review reply write with safe file-only input and read-back verification |
| Legacy v4.9 reviews (write) | `google-business-profile-safe-cli legacy-v49 accounts locations reviews delete-reply` | `implemented` | Legacy review reply delete with `--yes`, empty-body handling, and read-back verification |
| Legacy v4.9 transfer (write) | `google-business-profile-safe-cli legacy-v49 accounts locations transfer` | `implemented` | Deprecated legacy transfer with strict read-back verification against source and destination account location lists |
| Legacy v4.9 media follow-up (write) | `google-business-profile-safe-cli legacy-v49 accounts locations media start-upload` | `implemented` | Companion step that returns the Google upload resource reference |
| Legacy v4.9 media follow-up (write) | `google-business-profile-safe-cli legacy-v49 accounts locations media create` | `implemented` | Companion step that creates the location media record after upload |

## Full official boundary ledger

### Account Management API

Default status: `planned`, `access-gated`, `live-unverified`

Implemented in this slice:

- `accounts.get` -> `google-business-profile-safe-cli account-management accounts get` (`implemented`)
- `accounts.list` -> `google-business-profile-safe-cli account-management accounts list` (`implemented`)
- `accounts.admins.list` -> `google-business-profile-safe-cli account-management accounts admins list` (`implemented`)
- `accounts.invitations.accept` -> `google-business-profile-safe-cli account-management accounts invitations accept` (`implemented`)
- `accounts.invitations.decline` -> `google-business-profile-safe-cli account-management accounts invitations decline` (`implemented`)
- `accounts.invitations.list` -> `google-business-profile-safe-cli account-management accounts invitations list` (`implemented`)
- `locations.admins.list` -> `google-business-profile-safe-cli account-management locations admins list` (`implemented`)
- `accounts.create` -> `google-business-profile-safe-cli account-management accounts create` (`implemented`)
- `accounts.admins.create` -> `google-business-profile-safe-cli account-management accounts admins create` (`implemented`)
- `accounts.admins.delete` -> `google-business-profile-safe-cli account-management accounts admins delete` (`implemented`)
- `accounts.admins.patch` -> `google-business-profile-safe-cli account-management accounts admins patch` (`implemented`)
- `locations.admins.create` -> `google-business-profile-safe-cli account-management locations admins create` (`implemented`)
- `locations.admins.delete` -> `google-business-profile-safe-cli account-management locations admins delete` (`implemented`)
- `locations.admins.patch` -> `google-business-profile-safe-cli account-management locations admins patch` (`implemented`)
- `locations.transfer` -> `google-business-profile-safe-cli account-management locations transfer` (`implemented`)
- `accounts.patch` -> `google-business-profile-safe-cli account-management accounts patch` (`implemented`)

Notes:

- `accounts.admins.create` is shipped in a safe subset that requires the invitee email in `admin` and accepts only `OWNER` or `MANAGER`.
- `accounts.admins.patch` is shipped in a safe subset that updates only `role` and accepts only `OWNER` or `MANAGER`.
- `accounts.admins.delete` and the two write methods above verify the final state through `accounts.admins.list` before marking `changed=true`.
- `locations.admins.create` is shipped in a safe subset that allows exactly one identity field: `admin` (invitee email) or `account` (`accounts/{account}`), and accepts `OWNER`, `MANAGER`, or `SITE_MANAGER`.
- `locations.admins.patch` is shipped in a safe subset that updates only `role` and accepts `OWNER`, `MANAGER`, or `SITE_MANAGER`.
- `locations.admins.delete` and the two write methods above verify the final state through `locations.admins.list` before marking `changed=true`.
- `locations.transfer` uses business-info account location list read-back verification to ensure the location leaves source and appears in destination with paging handling for both source and destination lists.
- `locations.transfer` requires different `--source-account` and `--destination-account` values plus `--plan-in`, `--yes`, and `--ack-irreversible` on apply.

Planned in this section:

- all other account-management operations above remain `planned` until shipped in a later slice.

### Business Information API

Default status: `planned`, `access-gated`, `live-unverified`

Implemented in this slice:

- `accounts.locations.list` -> `google-business-profile-safe-cli business-info accounts locations list` (`implemented`)
- `locations.get` -> `google-business-profile-safe-cli business-info locations get` (`implemented`)
- `locations.getAttributes` -> `google-business-profile-safe-cli business-info locations get-attributes` (`implemented`)
- `locations.getGoogleUpdated` -> `google-business-profile-safe-cli business-info locations get-google-updated` (`implemented`)
- `locations.attributes.getGoogleUpdated` -> `google-business-profile-safe-cli business-info locations attributes get-google-updated` (`implemented`)
- `attributes.list` -> `google-business-profile-safe-cli business-info attributes list` (`implemented`)
- `accounts.locations.create` -> `google-business-profile-safe-cli business-info accounts locations create` (`implemented`)
- `categories.list` -> `google-business-profile-safe-cli business-info categories list` (`implemented`)
- `categories.batchGet` -> `google-business-profile-safe-cli business-info categories batch-get` (`implemented`)
- `chains.search` -> `google-business-profile-safe-cli business-info chains search` (`implemented`)
- `chains.get` -> `google-business-profile-safe-cli business-info chains get` (`implemented`)
- `googleLocations.search` -> `google-business-profile-safe-cli business-info google-locations search` (`implemented`)
- `locations.patch` -> `google-business-profile-safe-cli business-info locations patch` (`implemented`)
- `locations.updateAttributes` -> `google-business-profile-safe-cli business-info locations update-attributes` (`implemented`)
- `locations.delete` -> `google-business-profile-safe-cli business-info locations delete` (`implemented`)

Planned in this section:

- none (all Business Information methods in this slice are implemented)

### Lodging API

Default status: `implemented`, `access-gated`, `live-unverified`

Implemented in this slice:

- `locations.getLodging` -> `google-business-profile-safe-cli lodging locations get-lodging` (`implemented`)
- `locations.updateLodging` -> `google-business-profile-safe-cli lodging locations update-lodging` (`implemented`)
- `locations.lodging.getGoogleUpdated` -> `google-business-profile-safe-cli lodging locations lodging get-google-updated` (`implemented`)

### Notifications API

Default status: `implemented`, `access-gated`, `live-unverified`

Implemented in this slice:

- `accounts.getNotificationSetting` -> `google-business-profile-safe-cli notifications accounts get-notification-setting` (`implemented`)
- `accounts.updateNotificationSetting` -> `google-business-profile-safe-cli notifications accounts update-notification-setting` (`implemented`)

### Performance API

Default status: `implemented`, `access-gated`, `live-unverified`

Implemented in this slice:

- `locations.fetchMultiDailyMetricsTimeSeries` -> `google-business-profile-safe-cli performance locations fetch-multi-daily-metrics-time-series` (`implemented`)
- `locations.getDailyMetricsTimeSeries` -> `google-business-profile-safe-cli performance locations get-daily-metrics-time-series` (`implemented`)
- `locations.searchkeywords.impressions.monthly.list` -> `google-business-profile-safe-cli performance locations search-keywords impressions monthly list` (`implemented`)

Notes:
- `fetchMultiDailyMetricsTimeSeries` does not have official paging fields in the discovery document, so this CLI does not expose `pageSize` or `pageToken` for that method.
- The official discovery document lists `dailySubEntityType.*` query fields for `getDailyMetricsTimeSeries`, but Google also says sub-entity breakdowns are not currently supported for any metric, so this CLI does not expose those unsupported query fields.

### Place Actions API

Default status: `implemented`, `access-gated`, `live-unverified`

Implemented in this slice:

- `locations.placeActionLinks.create` -> `google-business-profile-safe-cli place-actions locations place-action-links create` (`implemented`)
- `locations.placeActionLinks.delete` -> `google-business-profile-safe-cli place-actions locations place-action-links delete` (`implemented`)
- `locations.placeActionLinks.get` -> `google-business-profile-safe-cli place-actions locations place-action-links get` (`implemented`)
- `locations.placeActionLinks.list` -> `google-business-profile-safe-cli place-actions locations place-action-links list` (`implemented`)
- `locations.placeActionLinks.patch` -> `google-business-profile-safe-cli place-actions locations place-action-links patch` (`implemented`)
- `placeActionTypeMetadata.list` -> `google-business-profile-safe-cli place-actions place-action-type-metadata list` (`implemented`)

### Verifications API

Default status: `implemented`, `access-gated`, `live-unverified`

Implemented in this slice:

- `locations.fetchVerificationOptions` -> `google-business-profile-safe-cli verifications locations fetch-verification-options` (`implemented`)
- `locations.getVoiceOfMerchantState` -> `google-business-profile-safe-cli verifications locations get-voice-of-merchant-state` (`implemented`)
- `locations.verifications.list` -> `google-business-profile-safe-cli verifications locations verifications list` (`implemented`)
- `locations.verify` -> `google-business-profile-safe-cli verifications locations verify` (`implemented`)
- `locations.verifications.complete` -> `google-business-profile-safe-cli verifications locations verifications complete` (`implemented`)
- `verificationTokens.generate` -> `google-business-profile-safe-cli verifications verification-tokens generate` (`implemented`)

Planned in this section:

- none (all Verifications methods in this slice are implemented)

Notes:
- `verificationTokens.generate` is not listed in the normal public REST overview but appears in discovery.
- This command is verified from response fields only, with no separate follow-up read method.
- The raw token is written only to `--verification-token-out` as `{"tokenString":"..."}` and is redacted everywhere else.

### Business Calls API

Default status: `implemented`, `access-gated`, `live-unverified`

Implemented in this slice:

- `locations.getBusinesscallssettings` -> `google-business-profile-safe-cli business-calls locations get-business-calls-settings` (`implemented`)
- `locations.updateBusinesscallssettings` -> `google-business-profile-safe-cli business-calls locations update-business-calls-settings` (`implemented`)
- `locations.businesscallsinsights.list` -> `google-business-profile-safe-cli business-calls locations business-calls-insights list` (`implemented`)

### Media upload v1

Default status: `implemented`, `live-unverified`

Implemented in this slice:

- `media.upload` -> `google-business-profile-safe-cli media-upload-v1 media upload` (`implemented`)

Notes:
- Google documents one method page with two URIs:
  - metadata upload path
  - binary upload path under `/upload/`
- Verification in this slice is by matching provider response `resourceName`; there is no direct read-back command for this family yet.
- The full bytes-to-location publishing flow now includes implemented legacy follow-up commands `accounts.locations.media.startUpload` and `accounts.locations.media.create`.

### Q&A API

Default status: `provider-discontinued`, `not-shipping`, `live-unverified`

Notes:
- Google discontinued this API on 2025-11-03.
- Keep it in the ledger for honesty.
- Do not count it as live-shippable command coverage unless Google restores a supported public surface.

- `locations.questions.create` -> `google-business-profile-safe-cli qanda locations questions create`
- `locations.questions.delete` -> `google-business-profile-safe-cli qanda locations questions delete`
- `locations.questions.list` -> `google-business-profile-safe-cli qanda locations questions list`
- `locations.questions.patch` -> `google-business-profile-safe-cli qanda locations questions patch`
- `locations.questions.answers.delete` -> `google-business-profile-safe-cli qanda locations questions answers delete`
- `locations.questions.answers.list` -> `google-business-profile-safe-cli qanda locations questions answers list`
- `locations.questions.answers.upsert` -> `google-business-profile-safe-cli qanda locations questions answers upsert`

### Legacy Google My Business `v4.9`

Default status: `planned`, `legacy-v49`, `live-unverified`

Notes:
- This is the remaining official legacy surface that still matters for an honest coverage claim.
- Some resources are deprecated in favor of newer specialized APIs.
- For question operations below, the provider-discontinued Q&A note overrides the default legacy status.

#### `accounts`

- `accounts.create` -> `google-business-profile-safe-cli legacy-v49 accounts create`
- `accounts.deleteNotifications` -> `google-business-profile-safe-cli legacy-v49 accounts delete-notifications`
- `accounts.generateAccountNumber` -> `google-business-profile-safe-cli legacy-v49 accounts generate-account-number`
- `accounts.get` -> `google-business-profile-safe-cli legacy-v49 accounts get`
- `accounts.getNotifications` -> `google-business-profile-safe-cli legacy-v49 accounts get-notifications`
- `accounts.list` -> `google-business-profile-safe-cli legacy-v49 accounts list`
- `accounts.listRecommendGoogleLocations` -> `google-business-profile-safe-cli legacy-v49 accounts list-recommend-google-locations`
- `accounts.update` -> `google-business-profile-safe-cli legacy-v49 accounts update`
- `accounts.updateNotifications` -> `google-business-profile-safe-cli legacy-v49 accounts update-notifications`

#### `accounts.admins`

- `accounts.admins.create` -> `google-business-profile-safe-cli legacy-v49 accounts admins create`
- `accounts.admins.delete` -> `google-business-profile-safe-cli legacy-v49 accounts admins delete`
- `accounts.admins.list` -> `google-business-profile-safe-cli legacy-v49 accounts admins list`
- `accounts.admins.patch` -> `google-business-profile-safe-cli legacy-v49 accounts admins patch`

#### `accounts.invitations`

- `accounts.invitations.accept` -> `google-business-profile-safe-cli legacy-v49 accounts invitations accept`
- `accounts.invitations.decline` -> `google-business-profile-safe-cli legacy-v49 accounts invitations decline`
- `accounts.invitations.list` -> `google-business-profile-safe-cli legacy-v49 accounts invitations list`

#### `accounts.locations`

- `accounts.locations.associate` -> `google-business-profile-safe-cli legacy-v49 accounts locations associate`
- `accounts.locations.batchGet` -> `google-business-profile-safe-cli legacy-v49 accounts locations batch-get`
- `accounts.locations.batchGetReviews` -> `google-business-profile-safe-cli legacy-v49 accounts locations batch-get-reviews`
- `accounts.locations.clearAssociation` -> `google-business-profile-safe-cli legacy-v49 accounts locations clear-association`
- `accounts.locations.create` -> `google-business-profile-safe-cli legacy-v49 accounts locations create`
- `accounts.locations.delete` -> `google-business-profile-safe-cli legacy-v49 accounts locations delete`
- `accounts.locations.fetchVerificationOptions` -> `google-business-profile-safe-cli legacy-v49 accounts locations fetch-verification-options`
- `accounts.locations.findMatches` -> `google-business-profile-safe-cli legacy-v49 accounts locations find-matches`
- `accounts.locations.get` -> `google-business-profile-safe-cli legacy-v49 accounts locations get`
- `accounts.locations.getFoodMenus` -> `google-business-profile-safe-cli legacy-v49 accounts locations get-food-menus`
- `accounts.locations.getGoogleUpdated` -> `google-business-profile-safe-cli legacy-v49 accounts locations get-google-updated`
- `accounts.locations.getHealthProviderAttributes` -> `google-business-profile-safe-cli legacy-v49 accounts locations get-health-provider-attributes`
- `accounts.locations.getServiceList` -> `google-business-profile-safe-cli legacy-v49 accounts locations get-service-list`
- `accounts.locations.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations list`
- `accounts.locations.patch` -> `google-business-profile-safe-cli legacy-v49 accounts locations patch`
- `accounts.locations.reportInsights` -> `google-business-profile-safe-cli legacy-v49 accounts locations report-insights`
- `accounts.locations.transfer` -> `google-business-profile-safe-cli legacy-v49 accounts locations transfer` (`implemented`)
- `accounts.locations.updateFoodMenus` -> `google-business-profile-safe-cli legacy-v49 accounts locations update-food-menus`
- `accounts.locations.updateHealthProviderAttributes` -> `google-business-profile-safe-cli legacy-v49 accounts locations update-health-provider-attributes`
- `accounts.locations.updateServiceList` -> `google-business-profile-safe-cli legacy-v49 accounts locations update-service-list`
- `accounts.locations.verify` -> `google-business-profile-safe-cli legacy-v49 accounts locations verify`

#### `accounts.locations.admins`

- `accounts.locations.admins.create` -> `google-business-profile-safe-cli legacy-v49 accounts locations admins create`
- `accounts.locations.admins.delete` -> `google-business-profile-safe-cli legacy-v49 accounts locations admins delete`
- `accounts.locations.admins.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations admins list`
- `accounts.locations.admins.patch` -> `google-business-profile-safe-cli legacy-v49 accounts locations admins patch`

#### `accounts.locations.followers`

- `accounts.locations.followers.getMetadata` -> `google-business-profile-safe-cli legacy-v49 accounts locations followers get-metadata`

#### `accounts.locations.insuranceNetworks`

- `accounts.locations.insuranceNetworks.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations insurance-networks list`

#### `accounts.locations.localPosts`

- `accounts.locations.localPosts.create` -> `google-business-profile-safe-cli legacy-v49 accounts locations local-posts create`
- `accounts.locations.localPosts.delete` -> `google-business-profile-safe-cli legacy-v49 accounts locations local-posts delete`
- `accounts.locations.localPosts.get` -> `google-business-profile-safe-cli legacy-v49 accounts locations local-posts get`
- `accounts.locations.localPosts.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations local-posts list`
- `accounts.locations.localPosts.patch` -> `google-business-profile-safe-cli legacy-v49 accounts locations local-posts patch`
- `accounts.locations.localPosts.reportInsights` -> `google-business-profile-safe-cli legacy-v49 accounts locations local-posts report-insights`

#### `accounts.locations.media`

Implemented in this slice:

- `accounts.locations.media.create` -> `google-business-profile-safe-cli legacy-v49 accounts locations media create` (`implemented`)
- `accounts.locations.media.startUpload` -> `google-business-profile-safe-cli legacy-v49 accounts locations media start-upload` (`implemented`)

Legacy transfer notes:

- `accounts.locations.transfer` is deprecated by Google in favor of the Account Management API, but it remains part of the official v4.9 surface and is shipped here for honest boundary coverage.
- `accounts.locations.transfer` requires `--plan-in`, `--yes`, and `--ack-irreversible` on apply, and `--to-account` must differ from the source account embedded in `--name`.
- `accounts.locations.transfer` verifies success by checking that `locations/{location}` disappears from the source account location list and appears in the destination account location list.

Still planned in this section:

- `accounts.locations.media.delete` -> `google-business-profile-safe-cli legacy-v49 accounts locations media delete`
- `accounts.locations.media.get` -> `google-business-profile-safe-cli legacy-v49 accounts locations media get`
- `accounts.locations.media.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations media list`
- `accounts.locations.media.patch` -> `google-business-profile-safe-cli legacy-v49 accounts locations media patch`

#### `accounts.locations.media.customers`

- `accounts.locations.media.customers.get` -> `google-business-profile-safe-cli legacy-v49 accounts locations media customers get`
- `accounts.locations.media.customers.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations media customers list`

#### `accounts.locations.questions`

Status override: `provider-discontinued`, `not-shipping`, `legacy-v49`, `live-unverified`

- `accounts.locations.questions.create` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions create`
- `accounts.locations.questions.delete` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions delete`
- `accounts.locations.questions.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions list`
- `accounts.locations.questions.patch` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions patch`

#### `accounts.locations.questions.answers`

Status override: `provider-discontinued`, `not-shipping`, `legacy-v49`, `live-unverified`

- `accounts.locations.questions.answers.delete` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions answers delete`
- `accounts.locations.questions.answers.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions answers list`
- `accounts.locations.questions.answers.upsert` -> `google-business-profile-safe-cli legacy-v49 accounts locations questions answers upsert`

#### `accounts.locations.reviews`

- `accounts.locations.reviews.deleteReply` -> `google-business-profile-safe-cli legacy-v49 accounts locations reviews delete-reply` (`implemented`)
- `accounts.locations.reviews.get` -> `google-business-profile-safe-cli legacy-v49 accounts locations reviews get` (`implemented`)
- `accounts.locations.reviews.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations reviews list` (`implemented`)
- `accounts.locations.reviews.updateReply` -> `google-business-profile-safe-cli legacy-v49 accounts locations reviews update-reply` (`implemented`)

Legacy reviews notes:

- `accounts.locations.reviews.list` validates `--page-size` to the official `1..50` range and accepts only the shipped official `--order-by` values: `rating`, `rating desc`, and `updateTime desc`.
- `accounts.locations.reviews.updateReply` is shipped in a safe subset that accepts only `--reply-file` JSON shaped exactly as `{"comment":"..."}` with a non-empty comment of 4096 bytes or fewer.
- `accounts.locations.reviews.updateReply` requires `--plan-in` on apply and verifies success by reading the review back and matching `reviewReply.comment`.
- `accounts.locations.reviews.deleteReply` requires `--plan-in` and `--yes` on apply, handles Google's empty-body delete response honestly, and verifies success by reading the review back and confirming `reviewReply` is absent.

#### `accounts.locations.verifications`

- `accounts.locations.verifications.complete` -> `google-business-profile-safe-cli legacy-v49 accounts locations verifications complete` (`implemented`)
- `accounts.locations.verifications.list` -> `google-business-profile-safe-cli legacy-v49 accounts locations verifications list` (`implemented`)

Legacy verification notes:

- `accounts.locations.verifications.list` is shipped as a read-only legacy companion to the specialized verifications family and uses the official legacy `pageSize` and `pageToken` query parameters.
- `accounts.locations.verifications.complete` accepts only `--pin-file` for the PIN, requires `--plan-in` on apply, and verifies success by listing the parent location verifications and confirming the completed verification state is `COMPLETED`.

#### Shared legacy resources

- `attributes.list` -> `google-business-profile-safe-cli legacy-v49 attributes list`
- `categories.batchGet` -> `google-business-profile-safe-cli legacy-v49 categories batch-get`
- `categories.list` -> `google-business-profile-safe-cli legacy-v49 categories list`
- `chains.get` -> `google-business-profile-safe-cli legacy-v49 chains get`
- `chains.search` -> `google-business-profile-safe-cli legacy-v49 chains search`
- `googleLocations.report` -> `google-business-profile-safe-cli legacy-v49 google-locations report`
- `googleLocations.search` -> `google-business-profile-safe-cli legacy-v49 google-locations search`

## Coverage decision for the next code slice

Next smallest bounded slice: `accounts.locations.batchGetReviews` -> `google-business-profile-safe-cli legacy-v49 accounts locations batch-get-reviews`
