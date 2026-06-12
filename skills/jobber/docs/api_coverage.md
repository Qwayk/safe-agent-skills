# Jobber API coverage ledger

## Official sources verified 2026-06-11
- API endpoint and request shape: https://developer.getjobber.com/docs/using_jobbers_api/api_queries_and_mutations/
- API versioning and required header: https://developer.getjobber.com/docs/using_jobbers_api/api_versioning/
- API rate limits: https://developer.getjobber.com/docs/using_jobbers_api/api_rate_limits/
- OAuth flows: https://developer.getjobber.com/docs/building_your_app/app_authorization/
- App lifecycle and disconnect: https://developer.getjobber.com/docs/building_your_app/app_lifecycle/
- Webhooks: https://developer.getjobber.com/docs/using_jobbers_api/setting_up_webhooks/
- Changelog (active versions): https://developer.getjobber.com/docs/changelog/
- Custom integration limits: https://developer.getjobber.com/docs/custom_integrations/
- Schema inventory source: docs/jobber_schema_inventory.json

## Jobber API baseline
- GraphQL endpoint: `POST https://api.getjobber.com/api/graphql`
- Request content type: `application/json`
- Authorization header: `Authorization: Bearer <ACCESS_TOKEN>`
- OAuth is required to obtain token and refresh token values.
- Header requirement: `X-JOBBER-GRAPHQL-VERSION` is required for all apps.
- Latest active version in changelog: `2025-04-16`.

## OAuth and token behavior
- Authorization endpoint: `GET https://api.getjobber.com/api/oauth/authorize`.
- Access and refresh tokens: `POST https://api.getjobber.com/api/oauth/token` with `grant_type=authorization_code`.
- Access token default expiration: 60 minutes.
- Refresh token can be used anytime before expiry to mint a new access token.
- Refresh Token Rotation OFF: same refresh token returned each time.
- Refresh Token Rotation ON: every refresh response returns a new token; previous token must not be reused.
- Reauthorization is required if both tokens are expired.

## Rate limits and query cost behavior
- Two limiters: DDoS middleware and GraphQL query cost.
- DDoS: 2500 requests per 5 minutes per app/account; over limit returns `429 Too Many Requests`.
- Cost model: query cost tracked with fields under `extensions.cost`.
  - `requestedQueryCost`, `actualQueryCost`, `throttleStatus.maximumAvailable`, `throttleStatus.currentlyAvailable`, `restoreRate`.
- Cost example values in docs show `maximumAvailable` currently `10000` and `restoreRate` `500` points/second.
- If `requestedQueryCost` exceeds `currentlyAvailable`, response is throttled (`code: THROTTLED`).

## Webhooks
- Webhook requests must be responded to within 1 second.
- Jobber may disable webhooks when response times miss the limit or errors requiring retries become frequent.
- Delivery is at-least-once; duplicates are possible and must be handled idempotently.
- Every request includes base64 `X-Jobber-Hmac-SHA256`; verify using app OAuth client secret and raw JSON payload.
- `APP_DISCONNECT` is part of disconnect handling flow and is required for marketplace disconnect verification.
- When a user disconnects in Jobber, tokens are invalidated and `APP_DISCONNECT` is emitted.

## Custom integration guardrail
- Draft Custom Integration apps can connect to up to 5 paying Jobber accounts.
- API access is blocked if Draft connects to more than 5 paying accounts.
- More than 5 requires Jobber approval.

## Runtime command policy
- Do not ship a raw Query/Mutation bridge.
- Command generation must be derived from operation registry.
- Command-family lock for implementation:
  - `auth`
  - `schema`
  - `read` (one named subcommand per Query field)
  - `write` (one named plan/apply subcommand per Mutation field)
  - `webhooks` (local helper, topic helpers, verification helper)
  - `jobs`
  - `runs`

## Coverage and status
- `shipped`: local helper foundation is implemented.
- `registry-backed/live-unverified/scope-gated`: command is generated from the official schema and tested offline, but live scope behavior is not verified.
- `registry-backed/live-unverified/scaffold-limited`: mutation command is generated from the official schema, plans and applies only through a reviewed plan, and is tested offline; per-mutation payload semantics, before-state snapshots, scope gating, and live provider effects remain unverified.
- `topic-listed/live-unverified`: webhook topic is listed and local signature verification exists, but live delivery is not verified.
- `access-gated/live-unverified`: requires live account scope/token to fully verify.

## Command-family status
| Command family | Status | Scope |
|---|---|---|
| `auth` | shipped | OAuth token helpers and form-encoded token refresh |
| `schema` | shipped | Inventory and operation registry source loading |
| `jobs` | shipped | CSV batch planning for `read.<JobberQuery>` and `write.<JobberMutation>` rows |
| `runs` | shipped | Local run listing/show helpers |
| `read` | registry-backed/live-unverified/scope-gated | Named read subcommands generated from Query fields |
| `write` | registry-backed/live-unverified/scaffold-limited | Named mutation subcommands generated from Mutation fields; apply requires reviewed `--plan-in` |
| `webhooks` | topic-listed/live-unverified | Topic discovery and local HMAC verification; endpoint delivery remains app-configured |

## Runtime implementation note

The CLI now loads `docs/jobber_schema_inventory.json` and creates one named `read` subcommand for every Query field and one named `write` subcommand for every Mutation field. These commands are explicit registry-backed commands, not a raw GraphQL bridge. Mutation commands create reviewed plans and only apply when `--plan-in` matches the current endpoint, mutation, arguments, selection, and GraphQL document. Live account behavior, account scopes, provider side effects, and per-mutation business verification remain `live-unverified`.

Write commands always include before-state metadata in every plan and receipt:
- `snapshot_status` is always `"No snapshot available"` for this runtime.
- `recovery_notes` and `recovery` fields explain that recovery may be manual or impossible.
- High-risk write operations (names with risky `delete`, `destroy`, `remove`, `cancel`, `archive`, send, payment/spend, auth, permission, bulk, and ownership terms) require `--ack-no-snapshot` before HTTP execution.
- Clearly irreversible operations, including destructive names and detectable send/payment/publish actions, also require `--ack-irreversible`.

## Query coverage ledger
| # | Query field | Planned command | Status |
|---|---|---|---|
|   1 | account | read account | registry-backed/live-unverified/scope-gated |
|   2 | accountAdditionalUserAddons | read accountAdditionalUserAddons | registry-backed/live-unverified/scope-gated |
|   3 | accountAddonInfo | read accountAddonInfo | registry-backed/live-unverified/scope-gated |
|   4 | accountAddonsInfo | read accountAddonsInfo | registry-backed/live-unverified/scope-gated |
|   5 | accountDeletionRequest | read accountDeletionRequest | registry-backed/live-unverified/scope-gated |
|   6 | accountFeatureFlag | read accountFeatureFlag | registry-backed/live-unverified/scope-gated |
|   7 | accountPlanInfo | read accountPlanInfo | registry-backed/live-unverified/scope-gated |
|   8 | accountPromotion | read accountPromotion | registry-backed/live-unverified/scope-gated |
|   9 | accountUnsafe | read accountUnsafe | registry-backed/live-unverified/scope-gated |
|  10 | accountingCodes | read accountingCodes | registry-backed/live-unverified/scope-gated |
|  11 | activityFeedData | read activityFeedData | registry-backed/live-unverified/scope-gated |
|  12 | activityFeedSettings | read activityFeedSettings | registry-backed/live-unverified/scope-gated |
|  13 | additionalUsersSubscription | read additionalUsersSubscription | registry-backed/live-unverified/scope-gated |
|  14 | addonDiscountGroup | read addonDiscountGroup | registry-backed/live-unverified/scope-gated |
|  15 | addonPreviewGroup | read addonPreviewGroup | registry-backed/live-unverified/scope-gated |
|  16 | aiAssistantClientCatalog | read aiAssistantClientCatalog | registry-backed/live-unverified/scope-gated |
|  17 | aiAssistantConversations | read aiAssistantConversations | registry-backed/live-unverified/scope-gated |
|  18 | aiAssistantFeatures | read aiAssistantFeatures | registry-backed/live-unverified/scope-gated |
|  19 | aiAssistantInsightWidgets | read aiAssistantInsightWidgets | registry-backed/live-unverified/scope-gated |
|  20 | aiAssistantMessages | read aiAssistantMessages | registry-backed/live-unverified/scope-gated |
|  21 | aiAssistantSkills | read aiAssistantSkills | registry-backed/live-unverified/scope-gated |
|  22 | aiAssistantUnifiedConversationHistory | read aiAssistantUnifiedConversationHistory | registry-backed/live-unverified/scope-gated |
|  23 | aiReceptionistCallLogsReport | read aiReceptionistCallLogsReport | registry-backed/live-unverified/scope-gated |
|  24 | aiReceptionistConversationFeedback | read aiReceptionistConversationFeedback | registry-backed/live-unverified/scope-gated |
|  25 | aiReceptionistForwardingCarrierLookup | read aiReceptionistForwardingCarrierLookup | registry-backed/live-unverified/scope-gated |
|  26 | aiReceptionistModalityUsageReport | read aiReceptionistModalityUsageReport | registry-backed/live-unverified/scope-gated |
|  27 | aiReceptionistSession | read aiReceptionistSession | registry-backed/live-unverified/scope-gated |
|  28 | aiReceptionistSettings | read aiReceptionistSettings | registry-backed/live-unverified/scope-gated |
|  29 | aiReceptionistSmsState | read aiReceptionistSmsState | registry-backed/live-unverified/scope-gated |
|  30 | aiReceptionistStates | read aiReceptionistStates | registry-backed/live-unverified/scope-gated |
|  31 | aiReceptionistUsageAndActivityReport | read aiReceptionistUsageAndActivityReport | registry-backed/live-unverified/scope-gated |
|  32 | aiReceptionistUsageAndActivityReportOutcomes | read aiReceptionistUsageAndActivityReportOutcomes | registry-backed/live-unverified/scope-gated |
|  33 | aiReceptionistUsageAndActivityReportTimeSavedKpis | read aiReceptionistUsageAndActivityReportTimeSavedKpis | registry-backed/live-unverified/scope-gated |
|  34 | appAlerts | read appAlerts | registry-backed/live-unverified/scope-gated |
|  35 | apps | read apps | registry-backed/live-unverified/scope-gated |
|  36 | assessment | read assessment | registry-backed/live-unverified/scope-gated |
|  37 | assessmentFormSubmission | read assessmentFormSubmission | registry-backed/live-unverified/scope-gated |
|  38 | assetBookkeepingAuthToken | read assetBookkeepingAuthToken | registry-backed/live-unverified/scope-gated |
|  39 | assetJournalEntryLineEntries | read assetJournalEntryLineEntries | registry-backed/live-unverified/scope-gated |
|  40 | attention | read attention | registry-backed/live-unverified/scope-gated |
|  41 | authorizeNetPaymentSettings | read authorizeNetPaymentSettings | registry-backed/live-unverified/scope-gated |
|  42 | automationDefaultActionMessage | read automationDefaultActionMessage | registry-backed/live-unverified/scope-gated |
|  43 | automationRule | read automationRule | registry-backed/live-unverified/scope-gated |
|  44 | automationRuleActionMessage | read automationRuleActionMessage | registry-backed/live-unverified/scope-gated |
|  45 | automationRuleBuilder | read automationRuleBuilder | registry-backed/live-unverified/scope-gated |
|  46 | automationRules | read automationRules | registry-backed/live-unverified/scope-gated |
|  47 | automationTasks | read automationTasks | registry-backed/live-unverified/scope-gated |
|  48 | availableBillingCountries | read availableBillingCountries | registry-backed/live-unverified/scope-gated |
|  49 | averageJobValue | read averageJobValue | registry-backed/live-unverified/scope-gated |
|  50 | backgroundWorker | read backgroundWorker | registry-backed/live-unverified/scope-gated |
|  51 | batchCardOnFile | read batchCardOnFile | registry-backed/live-unverified/scope-gated |
|  52 | billingPayments | read billingPayments | registry-backed/live-unverified/scope-gated |
|  53 | blankClient | read blankClient | registry-backed/live-unverified/scope-gated |
|  54 | blankUser | read blankUser | registry-backed/live-unverified/scope-gated |
|  55 | businessCoachingGoals | read businessCoachingGoals | registry-backed/live-unverified/scope-gated |
|  56 | businessHealthOverview | read businessHealthOverview | registry-backed/live-unverified/scope-gated |
|  57 | businessListing | read businessListing | registry-backed/live-unverified/scope-gated |
|  58 | businessListingsGoogleBusinessCategories | read businessListingsGoogleBusinessCategories | registry-backed/live-unverified/scope-gated |
|  59 | calendarStyles | read calendarStyles | registry-backed/live-unverified/scope-gated |
|  60 | callToAction | read callToAction | registry-backed/live-unverified/scope-gated |
|  61 | callToActions | read callToActions | registry-backed/live-unverified/scope-gated |
|  62 | capitalFinancingPromotion | read capitalFinancingPromotion | registry-backed/live-unverified/scope-gated |
|  63 | capitalHomeEntryPoint | read capitalHomeEntryPoint | registry-backed/live-unverified/scope-gated |
|  64 | capitalLendingAssociation | read capitalLendingAssociation | registry-backed/live-unverified/scope-gated |
|  65 | capitalLendingContext | read capitalLendingContext | registry-backed/live-unverified/scope-gated |
|  66 | capitalLendingOpportunityAssessment | read capitalLendingOpportunityAssessment | registry-backed/live-unverified/scope-gated |
|  67 | capitalLoans | read capitalLoans | registry-backed/live-unverified/scope-gated |
|  68 | capitalProduct | read capitalProduct | registry-backed/live-unverified/scope-gated |
|  69 | cardReaderConnectionToken | read cardReaderConnectionToken | registry-backed/live-unverified/scope-gated |
|  70 | catalogItem | read catalogItem | registry-backed/live-unverified/scope-gated |
|  71 | catalogItemCustomPricing | read catalogItemCustomPricing | registry-backed/live-unverified/scope-gated |
|  72 | catalogItems | read catalogItems | registry-backed/live-unverified/scope-gated |
|  73 | chemicalTreatmentSettings | read chemicalTreatmentSettings | registry-backed/live-unverified/scope-gated |
|  74 | client | read client | registry-backed/live-unverified/scope-gated |
|  75 | clientAutomatedReviewDetails | read clientAutomatedReviewDetails | registry-backed/live-unverified/scope-gated |
|  76 | clientBalanceOverview | read clientBalanceOverview | registry-backed/live-unverified/scope-gated |
|  77 | clientBalanceReport | read clientBalanceReport | registry-backed/live-unverified/scope-gated |
|  78 | clientEmails | read clientEmails | registry-backed/live-unverified/scope-gated |
|  79 | clientHubAccount | read clientHubAccount | registry-backed/live-unverified/scope-gated |
|  80 | clientHubReferralSettings | read clientHubReferralSettings | registry-backed/live-unverified/scope-gated |
|  81 | clientMeta | read clientMeta | registry-backed/live-unverified/scope-gated |
|  82 | clientNotification | read clientNotification | registry-backed/live-unverified/scope-gated |
|  83 | clientNotifications | read clientNotifications | registry-backed/live-unverified/scope-gated |
|  84 | clientPhone | read clientPhone | registry-backed/live-unverified/scope-gated |
|  85 | clientPhones | read clientPhones | registry-backed/live-unverified/scope-gated |
|  86 | clientPropertyCity | read clientPropertyCity | registry-backed/live-unverified/scope-gated |
|  87 | clientReengagement | read clientReengagement | registry-backed/live-unverified/scope-gated |
|  88 | clientTagUniqueLabels | read clientTagUniqueLabels | registry-backed/live-unverified/scope-gated |
|  89 | clients | read clients | registry-backed/live-unverified/scope-gated |
|  90 | clientsMetadata | read clientsMetadata | registry-backed/live-unverified/scope-gated |
|  91 | collectionNotes | read collectionNotes | registry-backed/live-unverified/scope-gated |
|  92 | commsAllClientsSegment | read commsAllClientsSegment | registry-backed/live-unverified/scope-gated |
|  93 | commsCampaign | read commsCampaign | registry-backed/live-unverified/scope-gated |
|  94 | commsCampaignCreators | read commsCampaignCreators | registry-backed/live-unverified/scope-gated |
|  95 | commsCampaignDefaultTemplate | read commsCampaignDefaultTemplate | registry-backed/live-unverified/scope-gated |
|  96 | commsCampaignPurchaseState | read commsCampaignPurchaseState | registry-backed/live-unverified/scope-gated |
|  97 | commsCampaignTemplates | read commsCampaignTemplates | registry-backed/live-unverified/scope-gated |
|  98 | commsCampaigns | read commsCampaigns | registry-backed/live-unverified/scope-gated |
|  99 | commsCampaignsExperience | read commsCampaignsExperience | registry-backed/live-unverified/scope-gated |
| 100 | commsEmailTemplates | read commsEmailTemplates | registry-backed/live-unverified/scope-gated |
| 101 | commsFilterSchemas | read commsFilterSchemas | registry-backed/live-unverified/scope-gated |
| 102 | commsPastClientsSegment | read commsPastClientsSegment | registry-backed/live-unverified/scope-gated |
| 103 | commsSmsTemplates | read commsSmsTemplates | registry-backed/live-unverified/scope-gated |
| 104 | commsUkKycRegistrationDetails | read commsUkKycRegistrationDetails | registry-backed/live-unverified/scope-gated |
| 105 | commsUpcomingClientsSegment | read commsUpcomingClientsSegment | registry-backed/live-unverified/scope-gated |
| 106 | communicationSettings | read communicationSettings | registry-backed/live-unverified/scope-gated |
| 107 | companySchedule | read companySchedule | registry-backed/live-unverified/scope-gated |
| 108 | consumableInfo | read consumableInfo | registry-backed/live-unverified/scope-gated |
| 109 | conversation | read conversation | registry-backed/live-unverified/scope-gated |
| 110 | conversations | read conversations | registry-backed/live-unverified/scope-gated |
| 111 | crews | read crews | registry-backed/live-unverified/scope-gated |
| 112 | customFieldConfigurations | read customFieldConfigurations | registry-backed/live-unverified/scope-gated |
| 113 | dailyJobRevenue | read dailyJobRevenue | registry-backed/live-unverified/scope-gated |
| 114 | delegateUser | read delegateUser | registry-backed/live-unverified/scope-gated |
| 115 | doubleBookings | read doubleBookings | registry-backed/live-unverified/scope-gated |
| 116 | ePaymentSavedCreditCards | read ePaymentSavedCreditCards | registry-backed/live-unverified/scope-gated |
| 117 | entriAuthToken | read entriAuthToken | registry-backed/live-unverified/scope-gated |
| 118 | event | read event | registry-backed/live-unverified/scope-gated |
| 119 | expense | read expense | registry-backed/live-unverified/scope-gated |
| 120 | expenseSuggestions | read expenseSuggestions | registry-backed/live-unverified/scope-gated |
| 121 | expenseUploadDocuments | read expenseUploadDocuments | registry-backed/live-unverified/scope-gated |
| 122 | expenseUploads | read expenseUploads | registry-backed/live-unverified/scope-gated |
| 123 | expenses | read expenses | registry-backed/live-unverified/scope-gated |
| 124 | experiment | read experiment | registry-backed/live-unverified/scope-gated |
| 125 | experiments | read experiments | registry-backed/live-unverified/scope-gated |
| 126 | expiringJobs | read expiringJobs | registry-backed/live-unverified/scope-gated |
| 127 | externalReminders | read externalReminders | registry-backed/live-unverified/scope-gated |
| 128 | feature | read feature | registry-backed/live-unverified/scope-gated |
| 129 | featureTrials | read featureTrials | registry-backed/live-unverified/scope-gated |
| 130 | featuresByCategory | read featuresByCategory | registry-backed/live-unverified/scope-gated |
| 131 | financialSnapshotMetrics | read financialSnapshotMetrics | registry-backed/live-unverified/scope-gated |
| 132 | flags | read flags | registry-backed/live-unverified/scope-gated |
| 133 | globalMessages | read globalMessages | registry-backed/live-unverified/scope-gated |
| 134 | googleBusinessAccount | read googleBusinessAccount | registry-backed/live-unverified/scope-gated |
| 135 | googlePlaceDetails | read googlePlaceDetails | registry-backed/live-unverified/scope-gated |
| 136 | googlePlacesAutocomplete | read googlePlacesAutocomplete | registry-backed/live-unverified/scope-gated |
| 137 | historicalConsumableInfos | read historicalConsumableInfos | registry-backed/live-unverified/scope-gated |
| 138 | homeFtux | read homeFtux | registry-backed/live-unverified/scope-gated |
| 139 | import | read import | registry-backed/live-unverified/scope-gated |
| 140 | importResults | read importResults | registry-backed/live-unverified/scope-gated |
| 141 | imports | read imports | registry-backed/live-unverified/scope-gated |
| 142 | inContextRecommendations | read inContextRecommendations | registry-backed/live-unverified/scope-gated |
| 143 | insightsAndAccountingProjectedIncome | read insightsAndAccountingProjectedIncome | registry-backed/live-unverified/scope-gated |
| 144 | insightsAndAccountingReceivables | read insightsAndAccountingReceivables | registry-backed/live-unverified/scope-gated |
| 145 | insightsAndAccountingRevenue | read insightsAndAccountingRevenue | registry-backed/live-unverified/scope-gated |
| 146 | invitedUser | read invitedUser | registry-backed/live-unverified/scope-gated |
| 147 | invoice | read invoice | registry-backed/live-unverified/scope-gated |
| 148 | invoiceDefaultCustomFieldValues | read invoiceDefaultCustomFieldValues | registry-backed/live-unverified/scope-gated |
| 149 | invoiceIssuedKpis | read invoiceIssuedKpis | registry-backed/live-unverified/scope-gated |
| 150 | invoicePastDueKpis | read invoicePastDueKpis | registry-backed/live-unverified/scope-gated |
| 151 | invoicePreview | read invoicePreview | registry-backed/live-unverified/scope-gated |
| 152 | invoiceReminder | read invoiceReminder | registry-backed/live-unverified/scope-gated |
| 153 | invoiceSample | read invoiceSample | registry-backed/live-unverified/scope-gated |
| 154 | invoiceSamples | read invoiceSamples | registry-backed/live-unverified/scope-gated |
| 155 | invoiceStatusOverview | read invoiceStatusOverview | registry-backed/live-unverified/scope-gated |
| 156 | invoices | read invoices | registry-backed/live-unverified/scope-gated |
| 157 | invoicesMetadata | read invoicesMetadata | registry-backed/live-unverified/scope-gated |
| 158 | invoicesReport | read invoicesReport | registry-backed/live-unverified/scope-gated |
| 159 | invoicesReportTotals | read invoicesReportTotals | registry-backed/live-unverified/scope-gated |
| 160 | job | read job | registry-backed/live-unverified/scope-gated |
| 161 | jobDefaultCustomFieldValues | read jobDefaultCustomFieldValues | registry-backed/live-unverified/scope-gated |
| 162 | jobForm | read jobForm | registry-backed/live-unverified/scope-gated |
| 163 | jobFormReportFormFieldColumns | read jobFormReportFormFieldColumns | registry-backed/live-unverified/scope-gated |
| 164 | jobForms | read jobForms | registry-backed/live-unverified/scope-gated |
| 165 | jobFormsReport | read jobFormsReport | registry-backed/live-unverified/scope-gated |
| 166 | jobKpis | read jobKpis | registry-backed/live-unverified/scope-gated |
| 167 | jobSamples | read jobSamples | registry-backed/live-unverified/scope-gated |
| 168 | jobberLabs | read jobberLabs | registry-backed/live-unverified/scope-gated |
| 169 | jobberPaymentsConfig | read jobberPaymentsConfig | registry-backed/live-unverified/scope-gated |
| 170 | jobberPaymentsDataSharingConsent | read jobberPaymentsDataSharingConsent | registry-backed/live-unverified/scope-gated |
| 171 | jobberPaymentsDialogSettings | read jobberPaymentsDialogSettings | registry-backed/live-unverified/scope-gated |
| 172 | jobberPaymentsDispute | read jobberPaymentsDispute | registry-backed/live-unverified/scope-gated |
| 173 | jobberPaymentsDisputes | read jobberPaymentsDisputes | registry-backed/live-unverified/scope-gated |
| 174 | jobberPaymentsFees | read jobberPaymentsFees | registry-backed/live-unverified/scope-gated |
| 175 | jobberPaymentsManagedAccount | read jobberPaymentsManagedAccount | registry-backed/live-unverified/scope-gated |
| 176 | jobberPaymentsMobileSignUpProgress | read jobberPaymentsMobileSignUpProgress | registry-backed/live-unverified/scope-gated |
| 177 | jobberPaymentsPaymentMethods | read jobberPaymentsPaymentMethods | registry-backed/live-unverified/scope-gated |
| 178 | jobberPaymentsPayouts | read jobberPaymentsPayouts | registry-backed/live-unverified/scope-gated |
| 179 | jobberPaymentsPayoutsSummary | read jobberPaymentsPayoutsSummary | registry-backed/live-unverified/scope-gated |
| 180 | jobberPaymentsSetting | read jobberPaymentsSetting | registry-backed/live-unverified/scope-gated |
| 181 | jobberPaymentsSettings | read jobberPaymentsSettings | registry-backed/live-unverified/scope-gated |
| 182 | jobberPaymentsUpcomingRequirementsDueCta | read jobberPaymentsUpcomingRequirementsDueCta | registry-backed/live-unverified/scope-gated |
| 183 | jobs | read jobs | registry-backed/live-unverified/scope-gated |
| 184 | jobsGoogleImportCalendarType | read jobsGoogleImportCalendarType | registry-backed/live-unverified/scope-gated |
| 185 | jobsImportProgress | read jobsImportProgress | registry-backed/live-unverified/scope-gated |
| 186 | jobsMetadata | read jobsMetadata | registry-backed/live-unverified/scope-gated |
| 187 | latestPositions | read latestPositions | registry-backed/live-unverified/scope-gated |
| 188 | latestReviewBenchmarks | read latestReviewBenchmarks | registry-backed/live-unverified/scope-gated |
| 189 | layerBookkeepingAuthToken | read layerBookkeepingAuthToken | registry-backed/live-unverified/scope-gated |
| 190 | leadFunnel | read leadFunnel | registry-backed/live-unverified/scope-gated |
| 191 | leadSourceSummaryReport | read leadSourceSummaryReport | registry-backed/live-unverified/scope-gated |
| 192 | leadSources | read leadSources | registry-backed/live-unverified/scope-gated |
| 193 | leadSourcesReport | read leadSourcesReport | registry-backed/live-unverified/scope-gated |
| 194 | liveSyncStats | read liveSyncStats | registry-backed/live-unverified/scope-gated |
| 195 | mapView | read mapView | registry-backed/live-unverified/scope-gated |
| 196 | marketingAccountConnections | read marketingAccountConnections | registry-backed/live-unverified/scope-gated |
| 197 | marketingCampaignStats | read marketingCampaignStats | registry-backed/live-unverified/scope-gated |
| 198 | marketingCampaignTotals | read marketingCampaignTotals | registry-backed/live-unverified/scope-gated |
| 199 | marketingClientReferralsSettings | read marketingClientReferralsSettings | registry-backed/live-unverified/scope-gated |
| 200 | marketingClientReferralsSourceLeadsDetails | read marketingClientReferralsSourceLeadsDetails | registry-backed/live-unverified/scope-gated |
| 201 | marketingClientReferralsSourceTotals | read marketingClientReferralsSourceTotals | registry-backed/live-unverified/scope-gated |
| 202 | marketingClientReferralsSources | read marketingClientReferralsSources | registry-backed/live-unverified/scope-gated |
| 203 | marketingDashboardHero | read marketingDashboardHero | registry-backed/live-unverified/scope-gated |
| 204 | marketingDashboardTopActions | read marketingDashboardTopActions | registry-backed/live-unverified/scope-gated |
| 205 | marketingItem | read marketingItem | registry-backed/live-unverified/scope-gated |
| 206 | marketingItemAuthors | read marketingItemAuthors | registry-backed/live-unverified/scope-gated |
| 207 | marketingItemJobShowcaseAuthors | read marketingItemJobShowcaseAuthors | registry-backed/live-unverified/scope-gated |
| 208 | marketingItems | read marketingItems | registry-backed/live-unverified/scope-gated |
| 209 | marketingRecommendedJobs | read marketingRecommendedJobs | registry-backed/live-unverified/scope-gated |
| 210 | marketingSourceAttribution | read marketingSourceAttribution | registry-backed/live-unverified/scope-gated |
| 211 | marketingStrategyPlan | read marketingStrategyPlan | registry-backed/live-unverified/scope-gated |
| 212 | marketingTopActions | read marketingTopActions | registry-backed/live-unverified/scope-gated |
| 213 | marketingTopPerformingCampaigns | read marketingTopPerformingCampaigns | registry-backed/live-unverified/scope-gated |
| 214 | marketingWebsiteAnalytics | read marketingWebsiteAnalytics | registry-backed/live-unverified/scope-gated |
| 215 | mediaLibrary | read mediaLibrary | registry-backed/live-unverified/scope-gated |
| 216 | mediaLibraryProvenance | read mediaLibraryProvenance | registry-backed/live-unverified/scope-gated |
| 217 | mobileBillingInfo | read mobileBillingInfo | registry-backed/live-unverified/scope-gated |
| 218 | moneyManagementAccount | read moneyManagementAccount | registry-backed/live-unverified/scope-gated |
| 219 | moneyManagementAccountStatementReport | read moneyManagementAccountStatementReport | registry-backed/live-unverified/scope-gated |
| 220 | moneyManagementCard | read moneyManagementCard | registry-backed/live-unverified/scope-gated |
| 221 | moneyManagementCardHolderCards | read moneyManagementCardHolderCards | registry-backed/live-unverified/scope-gated |
| 222 | moneyManagementCardHolders | read moneyManagementCardHolders | registry-backed/live-unverified/scope-gated |
| 223 | moneyManagementInactiveCard | read moneyManagementInactiveCard | registry-backed/live-unverified/scope-gated |
| 224 | moneyManagementPaymentMethods | read moneyManagementPaymentMethods | registry-backed/live-unverified/scope-gated |
| 225 | moneyManagementTransaction | read moneyManagementTransaction | registry-backed/live-unverified/scope-gated |
| 226 | moneyManagementTransactions | read moneyManagementTransactions | registry-backed/live-unverified/scope-gated |
| 227 | moneyManagementUsersEligibleForCards | read moneyManagementUsersEligibleForCards | registry-backed/live-unverified/scope-gated |
| 228 | myMentions | read myMentions | registry-backed/live-unverified/scope-gated |
| 229 | noteMentionEligibility | read noteMentionEligibility | registry-backed/live-unverified/scope-gated |
| 230 | onboarding | read onboarding | registry-backed/live-unverified/scope-gated |
| 231 | oneOffJobsReport | read oneOffJobsReport | registry-backed/live-unverified/scope-gated |
| 232 | oneOffJobsReportTotals | read oneOffJobsReportTotals | registry-backed/live-unverified/scope-gated |
| 233 | onlineBookingConfiguration | read onlineBookingConfiguration | registry-backed/live-unverified/scope-gated |
| 234 | onlineBookingGoogleSettings | read onlineBookingGoogleSettings | registry-backed/live-unverified/scope-gated |
| 235 | onlineBookingScheduleSettings | read onlineBookingScheduleSettings | registry-backed/live-unverified/scope-gated |
| 236 | onlineBookingService | read onlineBookingService | registry-backed/live-unverified/scope-gated |
| 237 | onlineBookingServices | read onlineBookingServices | registry-backed/live-unverified/scope-gated |
| 238 | openSupportConversations | read openSupportConversations | registry-backed/live-unverified/scope-gated |
| 239 | overdueItems | read overdueItems | registry-backed/live-unverified/scope-gated |
| 240 | paymentListItems | read paymentListItems | registry-backed/live-unverified/scope-gated |
| 241 | paymentMethods | read paymentMethods | registry-backed/live-unverified/scope-gated |
| 242 | paymentRecord | read paymentRecord | registry-backed/live-unverified/scope-gated |
| 243 | paymentRecords | read paymentRecords | registry-backed/live-unverified/scope-gated |
| 244 | paymentRefundReasons | read paymentRefundReasons | registry-backed/live-unverified/scope-gated |
| 245 | paymentTotalKpis | read paymentTotalKpis | registry-backed/live-unverified/scope-gated |
| 246 | paymentTypesByTotal | read paymentTypesByTotal | registry-backed/live-unverified/scope-gated |
| 247 | payoutRecord | read payoutRecord | registry-backed/live-unverified/scope-gated |
| 248 | payoutRecords | read payoutRecords | registry-backed/live-unverified/scope-gated |
| 249 | pdfSettings | read pdfSettings | registry-backed/live-unverified/scope-gated |
| 250 | phoneLookup | read phoneLookup | registry-backed/live-unverified/scope-gated |
| 251 | pipelineCardInsights | read pipelineCardInsights | registry-backed/live-unverified/scope-gated |
| 252 | pipelineCards | read pipelineCards | registry-backed/live-unverified/scope-gated |
| 253 | pipelineInsights | read pipelineInsights | registry-backed/live-unverified/scope-gated |
| 254 | pipelineStageRules | read pipelineStageRules | registry-backed/live-unverified/scope-gated |
| 255 | pipelineStages | read pipelineStages | registry-backed/live-unverified/scope-gated |
| 256 | pipelineTasks | read pipelineTasks | registry-backed/live-unverified/scope-gated |
| 257 | pipelines | read pipelines | registry-backed/live-unverified/scope-gated |
| 258 | plaidLinkAccountToken | read plaidLinkAccountToken | registry-backed/live-unverified/scope-gated |
| 259 | plaidLinkPaymentToken | read plaidLinkPaymentToken | registry-backed/live-unverified/scope-gated |
| 260 | planInfo | read planInfo | registry-backed/live-unverified/scope-gated |
| 261 | plansAvailable | read plansAvailable | registry-backed/live-unverified/scope-gated |
| 262 | preflightUserCreateMessage | read preflightUserCreateMessage | registry-backed/live-unverified/scope-gated |
| 263 | pricingCopyMobile | read pricingCopyMobile | registry-backed/live-unverified/scope-gated |
| 264 | product | read product | registry-backed/live-unverified/scope-gated |
| 265 | productByCatalogItem | read productByCatalogItem | registry-backed/live-unverified/scope-gated |
| 266 | productOrService | read productOrService | registry-backed/live-unverified/scope-gated |
| 267 | productOrServices | read productOrServices | registry-backed/live-unverified/scope-gated |
| 268 | products | read products | registry-backed/live-unverified/scope-gated |
| 269 | productsSearch | read productsSearch | registry-backed/live-unverified/scope-gated |
| 270 | properties | read properties | registry-backed/live-unverified/scope-gated |
| 271 | property | read property | registry-backed/live-unverified/scope-gated |
| 272 | propertyMergePreview | read propertyMergePreview | registry-backed/live-unverified/scope-gated |
| 273 | qboDaysSinceLastSync | read qboDaysSinceLastSync | registry-backed/live-unverified/scope-gated |
| 274 | quote | read quote | registry-backed/live-unverified/scope-gated |
| 275 | quoteDefaultCustomFieldValues | read quoteDefaultCustomFieldValues | registry-backed/live-unverified/scope-gated |
| 276 | quoteReminder | read quoteReminder | registry-backed/live-unverified/scope-gated |
| 277 | quoteStatusOverview | read quoteStatusOverview | registry-backed/live-unverified/scope-gated |
| 278 | quoteTemplate | read quoteTemplate | registry-backed/live-unverified/scope-gated |
| 279 | quoteTemplates | read quoteTemplates | registry-backed/live-unverified/scope-gated |
| 280 | quotes | read quotes | registry-backed/live-unverified/scope-gated |
| 281 | quotesMetadata | read quotesMetadata | registry-backed/live-unverified/scope-gated |
| 282 | quotesReport | read quotesReport | registry-backed/live-unverified/scope-gated |
| 283 | recentlyUpdatedClientsAndWorkObjects | read recentlyUpdatedClientsAndWorkObjects | registry-backed/live-unverified/scope-gated |
| 284 | recurringJobsReport | read recurringJobsReport | registry-backed/live-unverified/scope-gated |
| 285 | recurringRevenueTotals | read recurringRevenueTotals | registry-backed/live-unverified/scope-gated |
| 286 | referralDetails | read referralDetails | registry-backed/live-unverified/scope-gated |
| 287 | replyToOwnership | read replyToOwnership | registry-backed/live-unverified/scope-gated |
| 288 | request | read request | registry-backed/live-unverified/scope-gated |
| 289 | requestKpis | read requestKpis | registry-backed/live-unverified/scope-gated |
| 290 | requestReport | read requestReport | registry-backed/live-unverified/scope-gated |
| 291 | requestReportFormFieldColumns | read requestReportFormFieldColumns | registry-backed/live-unverified/scope-gated |
| 292 | requestSettings | read requestSettings | registry-backed/live-unverified/scope-gated |
| 293 | requestSettingsCollection | read requestSettingsCollection | registry-backed/live-unverified/scope-gated |
| 294 | requests | read requests | registry-backed/live-unverified/scope-gated |
| 295 | requestsConfiguration | read requestsConfiguration | registry-backed/live-unverified/scope-gated |
| 296 | requestsMetadata | read requestsMetadata | registry-backed/live-unverified/scope-gated |
| 297 | revenueByLocation | read revenueByLocation | registry-backed/live-unverified/scope-gated |
| 298 | revenueByPeriod | read revenueByPeriod | registry-backed/live-unverified/scope-gated |
| 299 | revenueCalculation | read revenueCalculation | registry-backed/live-unverified/scope-gated |
| 300 | revenueGoals | read revenueGoals | registry-backed/live-unverified/scope-gated |
| 301 | reviews | read reviews | registry-backed/live-unverified/scope-gated |
| 302 | reviewsCommsSummary | read reviewsCommsSummary | registry-backed/live-unverified/scope-gated |
| 303 | reviewsInitialMessageSettings | read reviewsInitialMessageSettings | registry-backed/live-unverified/scope-gated |
| 304 | rqjiWorkflowNextActions | read rqjiWorkflowNextActions | registry-backed/live-unverified/scope-gated |
| 305 | salesPipelineBriefStats | read salesPipelineBriefStats | registry-backed/live-unverified/scope-gated |
| 306 | salesPipelineSearch | read salesPipelineSearch | registry-backed/live-unverified/scope-gated |
| 307 | salesResultsTotals | read salesResultsTotals | registry-backed/live-unverified/scope-gated |
| 308 | salesResultsWonLost | read salesResultsWonLost | registry-backed/live-unverified/scope-gated |
| 309 | salespersonReport | read salespersonReport | registry-backed/live-unverified/scope-gated |
| 310 | scheduledItems | read scheduledItems | registry-backed/live-unverified/scope-gated |
| 311 | scheduledItemsAggregateTotals | read scheduledItemsAggregateTotals | registry-backed/live-unverified/scope-gated |
| 312 | scheduledTaskConversations | read scheduledTaskConversations | registry-backed/live-unverified/scope-gated |
| 313 | schedulingAssignmentSettings | read schedulingAssignmentSettings | registry-backed/live-unverified/scope-gated |
| 314 | schedulingAvailability | read schedulingAvailability | registry-backed/live-unverified/scope-gated |
| 315 | search | read search | registry-backed/live-unverified/scope-gated |
| 316 | secureDocumentRequest | read secureDocumentRequest | registry-backed/live-unverified/scope-gated |
| 317 | selfServeEligibility | read selfServeEligibility | registry-backed/live-unverified/scope-gated |
| 318 | setupExperience | read setupExperience | registry-backed/live-unverified/scope-gated |
| 319 | setupGuideCurrent | read setupGuideCurrent | registry-backed/live-unverified/scope-gated |
| 320 | similarClients | read similarClients | registry-backed/live-unverified/scope-gated |
| 321 | socialMarketingItems | read socialMarketingItems | registry-backed/live-unverified/scope-gated |
| 322 | socialMediaPost | read socialMediaPost | registry-backed/live-unverified/scope-gated |
| 323 | spEngagementMeetingAvailability | read spEngagementMeetingAvailability | registry-backed/live-unverified/scope-gated |
| 324 | stripeFileLink | read stripeFileLink | registry-backed/live-unverified/scope-gated |
| 325 | stripeProviderContext | read stripeProviderContext | registry-backed/live-unverified/scope-gated |
| 326 | subscriptionDiscount | read subscriptionDiscount | registry-backed/live-unverified/scope-gated |
| 327 | subscriptionDiscountGroup | read subscriptionDiscountGroup | registry-backed/live-unverified/scope-gated |
| 328 | subscriptionPause | read subscriptionPause | registry-backed/live-unverified/scope-gated |
| 329 | subscriptionPermissions | read subscriptionPermissions | registry-backed/live-unverified/scope-gated |
| 330 | subscriptionPreviewGroup | read subscriptionPreviewGroup | registry-backed/live-unverified/scope-gated |
| 331 | supplierAccountConnectionStatus | read supplierAccountConnectionStatus | registry-backed/live-unverified/scope-gated |
| 332 | supplierInvoiceBatches | read supplierInvoiceBatches | registry-backed/live-unverified/scope-gated |
| 333 | surchargePaymentDetails | read surchargePaymentDetails | registry-backed/live-unverified/scope-gated |
| 334 | syncObjectStats | read syncObjectStats | registry-backed/live-unverified/scope-gated |
| 335 | tapToPayIosConsent | read tapToPayIosConsent | registry-backed/live-unverified/scope-gated |
| 336 | task | read task | registry-backed/live-unverified/scope-gated |
| 337 | tasks | read tasks | registry-backed/live-unverified/scope-gated |
| 338 | taxRates | read taxRates | registry-backed/live-unverified/scope-gated |
| 339 | teamProductivityReport | read teamProductivityReport | registry-backed/live-unverified/scope-gated |
| 340 | thirdPartyPaymentSettings | read thirdPartyPaymentSettings | registry-backed/live-unverified/scope-gated |
| 341 | timeSheetAuditEvents | read timeSheetAuditEvents | registry-backed/live-unverified/scope-gated |
| 342 | timeSheetEntries | read timeSheetEntries | registry-backed/live-unverified/scope-gated |
| 343 | timeSheetEntriesByGroup | read timeSheetEntriesByGroup | registry-backed/live-unverified/scope-gated |
| 344 | timeSheetEntry | read timeSheetEntry | registry-backed/live-unverified/scope-gated |
| 345 | timeToApproveQuotes | read timeToApproveQuotes | registry-backed/live-unverified/scope-gated |
| 346 | timeToConvertLeads | read timeToConvertLeads | registry-backed/live-unverified/scope-gated |
| 347 | topClientsBalance | read topClientsBalance | registry-backed/live-unverified/scope-gated |
| 348 | topLeadSourcesByRevenue | read topLeadSourcesByRevenue | registry-backed/live-unverified/scope-gated |
| 349 | travelEstimate | read travelEstimate | registry-backed/live-unverified/scope-gated |
| 350 | trialStatus | read trialStatus | registry-backed/live-unverified/scope-gated |
| 351 | twilioCarrierRegistrationData | read twilioCarrierRegistrationData | registry-backed/live-unverified/scope-gated |
| 352 | unreadConversations | read unreadConversations | registry-backed/live-unverified/scope-gated |
| 353 | uploadAuthorization | read uploadAuthorization | registry-backed/live-unverified/scope-gated |
| 354 | user | read user | registry-backed/live-unverified/scope-gated |
| 355 | userBookingSchedule | read userBookingSchedule | registry-backed/live-unverified/scope-gated |
| 356 | userPermissionPreset | read userPermissionPreset | registry-backed/live-unverified/scope-gated |
| 357 | users | read users | registry-backed/live-unverified/scope-gated |
| 358 | vehicle | read vehicle | registry-backed/live-unverified/scope-gated |
| 359 | vehicles | read vehicles | registry-backed/live-unverified/scope-gated |
| 360 | viewSchedulingRecommendations | read viewSchedulingRecommendations | registry-backed/live-unverified/scope-gated |
| 361 | viewWebClientInsights | read viewWebClientInsights | registry-backed/live-unverified/scope-gated |
| 362 | viewWebJob | read viewWebJob | registry-backed/live-unverified/scope-gated |
| 363 | viewWebOneOffJobProfitAndLoss | read viewWebOneOffJobProfitAndLoss | registry-backed/live-unverified/scope-gated |
| 364 | viewWebOneOffJobsInsights | read viewWebOneOffJobsInsights | registry-backed/live-unverified/scope-gated |
| 365 | viewWebQuoteConversionInsights | read viewWebQuoteConversionInsights | registry-backed/live-unverified/scope-gated |
| 366 | viewWebSchedule | read viewWebSchedule | registry-backed/live-unverified/scope-gated |
| 367 | visit | read visit | registry-backed/live-unverified/scope-gated |
| 368 | visitFormSubmission | read visitFormSubmission | registry-backed/live-unverified/scope-gated |
| 369 | visitTotals | read visitTotals | registry-backed/live-unverified/scope-gated |
| 370 | visits | read visits | registry-backed/live-unverified/scope-gated |
| 371 | visitsReport | read visitsReport | registry-backed/live-unverified/scope-gated |
| 372 | waypoints | read waypoints | registry-backed/live-unverified/scope-gated |
| 373 | weatherForecast | read weatherForecast | registry-backed/live-unverified/scope-gated |
| 374 | webHookEvent | read webHookEvent | registry-backed/live-unverified/scope-gated |
| 375 | webhookSubscriptions | read webhookSubscriptions | registry-backed/live-unverified/scope-gated |
| 376 | websiteConfiguration | read websiteConfiguration | registry-backed/live-unverified/scope-gated |
| 377 | websiteDefaultImages | read websiteDefaultImages | registry-backed/live-unverified/scope-gated |
| 378 | wisetackCalculationData | read wisetackCalculationData | registry-backed/live-unverified/scope-gated |
| 379 | wisetackPaymentLink | read wisetackPaymentLink | registry-backed/live-unverified/scope-gated |
| 380 | wisetackPromo | read wisetackPromo | registry-backed/live-unverified/scope-gated |
| 381 | workItemData | read workItemData | registry-backed/live-unverified/scope-gated |
| 382 | workItemInitialSearch | read workItemInitialSearch | registry-backed/live-unverified/scope-gated |
| 383 | workItemSearch | read workItemSearch | registry-backed/live-unverified/scope-gated |
| 384 | workObjectGlobalOwnerships | read workObjectGlobalOwnerships | registry-backed/live-unverified/scope-gated |

## Mutation coverage ledger
| # | Mutation field | Planned command | Status |
|---|---|---|---|
|   1 | acceptInvitation | write acceptInvitation plan/apply | registry-backed/live-unverified/scaffold-limited |
|   2 | accountDeletionRequestCreate | write accountDeletionRequestCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|   3 | accountEditCompanyDetails | write accountEditCompanyDetails plan/apply | registry-backed/live-unverified/scaffold-limited |
|   4 | achPayment | write achPayment plan/apply | registry-backed/live-unverified/scaffold-limited |
|   5 | activationChecklistDismiss | write activationChecklistDismiss plan/apply | registry-backed/live-unverified/scaffold-limited |
|   6 | additionalUsersSubscriptionCreate | write additionalUsersSubscriptionCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|   7 | additionalUsersSubscriptionTerminate | write additionalUsersSubscriptionTerminate plan/apply | registry-backed/live-unverified/scaffold-limited |
|   8 | aiAssistantActionFollowupsDelete | write aiAssistantActionFollowupsDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
|   9 | aiAssistantClientConversationStore | write aiAssistantClientConversationStore plan/apply | registry-backed/live-unverified/scaffold-limited |
|  10 | aiAssistantContextHandOff | write aiAssistantContextHandOff plan/apply | registry-backed/live-unverified/scaffold-limited |
|  11 | aiAssistantDelegate | write aiAssistantDelegate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  12 | aiAssistantExecuteTool | write aiAssistantExecuteTool plan/apply | registry-backed/live-unverified/scaffold-limited |
|  13 | aiAssistantFeedbackCreate | write aiAssistantFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  14 | aiAssistantLoad | write aiAssistantLoad plan/apply | registry-backed/live-unverified/scaffold-limited |
|  15 | aiAssistantPrompt | write aiAssistantPrompt plan/apply | registry-backed/live-unverified/scaffold-limited |
|  16 | aiAssistantSupportEscalationInteractionUpdate | write aiAssistantSupportEscalationInteractionUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  17 | aiAssistantTextRevise | write aiAssistantTextRevise plan/apply | registry-backed/live-unverified/scaffold-limited |
|  18 | aiReceptionistBulkSessionStatusUpdate | write aiReceptionistBulkSessionStatusUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  19 | aiReceptionistCallForwardingGuideComplete | write aiReceptionistCallForwardingGuideComplete plan/apply | registry-backed/live-unverified/scaffold-limited |
|  20 | aiReceptionistCallRoutingRulesUpdate | write aiReceptionistCallRoutingRulesUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  21 | aiReceptionistChatConversationCreate | write aiReceptionistChatConversationCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  22 | aiReceptionistConversationFeedbackCreate | write aiReceptionistConversationFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  23 | aiReceptionistEmailDraftConfirm | write aiReceptionistEmailDraftConfirm plan/apply | registry-backed/live-unverified/scaffold-limited |
|  24 | aiReceptionistEmailDraftEdit | write aiReceptionistEmailDraftEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  25 | aiReceptionistEmailDraftReject | write aiReceptionistEmailDraftReject plan/apply | registry-backed/live-unverified/scaffold-limited |
|  26 | aiReceptionistFeedbackCreate | write aiReceptionistFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  27 | aiReceptionistGreetingCreate | write aiReceptionistGreetingCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  28 | aiReceptionistGreetingEdit | write aiReceptionistGreetingEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  29 | aiReceptionistSettingsEdit | write aiReceptionistSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  30 | aiReceptionistSettingsSetup | write aiReceptionistSettingsSetup plan/apply | registry-backed/live-unverified/scaffold-limited |
|  31 | aiReceptionistSmsStateEdit | write aiReceptionistSmsStateEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  32 | annualRevenueGoalSet | write annualRevenueGoalSet plan/apply | registry-backed/live-unverified/scaffold-limited |
|  33 | appAlertEdit | write appAlertEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  34 | appDisconnect | write appDisconnect plan/apply | registry-backed/live-unverified/scaffold-limited |
|  35 | appInstanceLastSyncDateEdit | write appInstanceLastSyncDateEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  36 | appRemove | write appRemove plan/apply | registry-backed/live-unverified/scaffold-limited |
|  37 | appRequestCreate | write appRequestCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  38 | appointmentEditAssignment | write appointmentEditAssignment plan/apply | registry-backed/live-unverified/scaffold-limited |
|  39 | appointmentEditCompleteness | write appointmentEditCompleteness plan/apply | registry-backed/live-unverified/scaffold-limited |
|  40 | appointmentEditSchedule | write appointmentEditSchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
|  41 | arrivalWindowsSettingsEdit | write arrivalWindowsSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  42 | assessmentComplete | write assessmentComplete plan/apply | registry-backed/live-unverified/scaffold-limited |
|  43 | assessmentCreate | write assessmentCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  44 | assessmentCreateWaypoint | write assessmentCreateWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
|  45 | assessmentDelete | write assessmentDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
|  46 | assessmentEdit | write assessmentEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  47 | assessmentFormSubmission | write assessmentFormSubmission plan/apply | registry-backed/live-unverified/scaffold-limited |
|  48 | assessmentStartTimer | write assessmentStartTimer plan/apply | registry-backed/live-unverified/scaffold-limited |
|  49 | assessmentStopTimer | write assessmentStopTimer plan/apply | registry-backed/live-unverified/scaffold-limited |
|  50 | assessmentUncomplete | write assessmentUncomplete plan/apply | registry-backed/live-unverified/scaffold-limited |
|  51 | assetBookkeepingConfigurationUpdate | write assetBookkeepingConfigurationUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  52 | assignAndGetExperimentStatus | write assignAndGetExperimentStatus plan/apply | registry-backed/live-unverified/scaffold-limited |
|  53 | automationFeedbackCreate | write automationFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  54 | automationRuleActionMessageEdit | write automationRuleActionMessageEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  55 | automationRuleActivate | write automationRuleActivate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  56 | automationRuleCreate | write automationRuleCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  57 | automationRuleCreateFromTemplate | write automationRuleCreateFromTemplate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  58 | automationRuleCreateWithType | write automationRuleCreateWithType plan/apply | registry-backed/live-unverified/scaffold-limited |
|  59 | automationRuleDeactivate | write automationRuleDeactivate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  60 | automationRuleEdit | write automationRuleEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  61 | automationRuleEditWithType | write automationRuleEditWithType plan/apply | registry-backed/live-unverified/scaffold-limited |
|  62 | batchCardOnFileRequesterCreate | write batchCardOnFileRequesterCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  63 | billingInfoEdit | write billingInfoEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  64 | billingInvoicePay | write billingInvoicePay plan/apply | registry-backed/live-unverified/scaffold-limited |
|  65 | bookSpEngagementMeeting | write bookSpEngagementMeeting plan/apply | registry-backed/live-unverified/scaffold-limited |
|  66 | bookkeepingRequestDemo | write bookkeepingRequestDemo plan/apply | registry-backed/live-unverified/scaffold-limited |
|  67 | bulkEnablePaymentPermission | write bulkEnablePaymentPermission plan/apply | registry-backed/live-unverified/scaffold-limited |
|  68 | bulkRescheduleAndReassign | write bulkRescheduleAndReassign plan/apply | registry-backed/live-unverified/scaffold-limited |
|  69 | businessCoachingSetGoals | write businessCoachingSetGoals plan/apply | registry-backed/live-unverified/scaffold-limited |
|  70 | businessListingsGoogleProfileEdit | write businessListingsGoogleProfileEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  71 | campaignActivate | write campaignActivate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  72 | campaignCheckFromEmailValidationCode | write campaignCheckFromEmailValidationCode plan/apply | registry-backed/live-unverified/scaffold-limited |
|  73 | campaignCreateAllClients | write campaignCreateAllClients plan/apply | registry-backed/live-unverified/scaffold-limited |
|  74 | campaignCreatePastClients | write campaignCreatePastClients plan/apply | registry-backed/live-unverified/scaffold-limited |
|  75 | campaignCreateTemplates | write campaignCreateTemplates plan/apply | registry-backed/live-unverified/scaffold-limited |
|  76 | campaignCreateUpcomingClients | write campaignCreateUpcomingClients plan/apply | registry-backed/live-unverified/scaffold-limited |
|  77 | campaignDelete | write campaignDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
|  78 | campaignDuplicate | write campaignDuplicate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  79 | campaignGeneration | write campaignGeneration plan/apply | registry-backed/live-unverified/scaffold-limited |
|  80 | campaignRequestFromEmailValidationCode | write campaignRequestFromEmailValidationCode plan/apply | registry-backed/live-unverified/scaffold-limited |
|  81 | campaignSegmentUpdateAllClients | write campaignSegmentUpdateAllClients plan/apply | registry-backed/live-unverified/scaffold-limited |
|  82 | campaignSegmentUpdatePastClients | write campaignSegmentUpdatePastClients plan/apply | registry-backed/live-unverified/scaffold-limited |
|  83 | campaignSegmentUpdateUpcomingClients | write campaignSegmentUpdateUpcomingClients plan/apply | registry-backed/live-unverified/scaffold-limited |
|  84 | campaignSend | write campaignSend plan/apply | registry-backed/live-unverified/scaffold-limited |
|  85 | campaignSendTestEmail | write campaignSendTestEmail plan/apply | registry-backed/live-unverified/scaffold-limited |
|  86 | campaignSendTestEmailForDemo | write campaignSendTestEmailForDemo plan/apply | registry-backed/live-unverified/scaffold-limited |
|  87 | campaignStatusUpdate | write campaignStatusUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  88 | campaignUpdateTemplates | write campaignUpdateTemplates plan/apply | registry-backed/live-unverified/scaffold-limited |
|  89 | cancelOwnershipTransfer | write cancelOwnershipTransfer plan/apply | registry-backed/live-unverified/scaffold-limited |
|  90 | cardReaderLocation | write cardReaderLocation plan/apply | registry-backed/live-unverified/scaffold-limited |
|  91 | clientArchive | write clientArchive plan/apply | registry-backed/live-unverified/scaffold-limited |
|  92 | clientAutomatedReviewDetailsEdit | write clientAutomatedReviewDetailsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
|  93 | clientBalanceReportExportCsv | write clientBalanceReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
|  94 | clientBulkAddTags | write clientBulkAddTags plan/apply | registry-backed/live-unverified/scaffold-limited |
|  95 | clientBulkDestroyTags | write clientBulkDestroyTags plan/apply | registry-backed/live-unverified/scaffold-limited |
|  96 | clientCreate | write clientCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
|  97 | clientCreateNote | write clientCreateNote plan/apply | registry-backed/live-unverified/scaffold-limited |
|  98 | clientCreateNoteWaypoint | write clientCreateNoteWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
|  99 | clientCreatePaymentRecord | write clientCreatePaymentRecord plan/apply | registry-backed/live-unverified/scaffold-limited |
| 100 | clientDelete | write clientDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 101 | clientDeleteNote | write clientDeleteNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 102 | clientEdit | write clientEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 103 | clientEditNote | write clientEditNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 104 | clientExport | write clientExport plan/apply | registry-backed/live-unverified/scaffold-limited |
| 105 | clientHubAccountEdit | write clientHubAccountEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 106 | clientHubAccountPermissionUpdate | write clientHubAccountPermissionUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 107 | clientHubReferralSettingsUpsert | write clientHubReferralSettingsUpsert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 108 | clientHubSurchargingFeedbackCreate | write clientHubSurchargingFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 109 | clientMergeCreate | write clientMergeCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 110 | clientNoteAddAttachment | write clientNoteAddAttachment plan/apply | registry-backed/live-unverified/scaffold-limited |
| 111 | clientUnarchive | write clientUnarchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 112 | clientsCreate | write clientsCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 113 | clientsDelete | write clientsDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 114 | clientsEditTags | write clientsEditTags plan/apply | registry-backed/live-unverified/scaffold-limited |
| 115 | clientsImport | write clientsImport plan/apply | registry-backed/live-unverified/scaffold-limited |
| 116 | clientsImportRevert | write clientsImportRevert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 117 | collectionNoteCreate | write collectionNoteCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 118 | collectionNoteEdit | write collectionNoteEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 119 | commsUkKycRegistrationContinue | write commsUkKycRegistrationContinue plan/apply | registry-backed/live-unverified/scaffold-limited |
| 120 | commsUkKycRegistrationCreate | write commsUkKycRegistrationCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 121 | commsUkKycRegistrationUpdate | write commsUkKycRegistrationUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 122 | companyProfileGenerateProfile | write companyProfileGenerateProfile plan/apply | registry-backed/live-unverified/scaffold-limited |
| 123 | companyProfileUpdate | write companyProfileUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 124 | confirmPayment | write confirmPayment plan/apply | registry-backed/live-unverified/scaffold-limited |
| 125 | connectPlaidBankAccount | write connectPlaidBankAccount plan/apply | registry-backed/live-unverified/scaffold-limited |
| 126 | consumableSetUsageOverLimit | write consumableSetUsageOverLimit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 127 | consumableSetUsageOverLimitDisabled | write consumableSetUsageOverLimitDisabled plan/apply | registry-backed/live-unverified/scaffold-limited |
| 128 | consumableSetUsageOverLimitUnlimited | write consumableSetUsageOverLimitUnlimited plan/apply | registry-backed/live-unverified/scaffold-limited |
| 129 | conversationDelete | write conversationDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 130 | conversationRead | write conversationRead plan/apply | registry-backed/live-unverified/scaffold-limited |
| 131 | conversationReassign | write conversationReassign plan/apply | registry-backed/live-unverified/scaffold-limited |
| 132 | conversationUnread | write conversationUnread plan/apply | registry-backed/live-unverified/scaffold-limited |
| 133 | createAutomatedCampaign | write createAutomatedCampaign plan/apply | registry-backed/live-unverified/scaffold-limited |
| 134 | createDefaultCampaign | write createDefaultCampaign plan/apply | registry-backed/live-unverified/scaffold-limited |
| 135 | createParafinBearerToken | write createParafinBearerToken plan/apply | registry-backed/live-unverified/scaffold-limited |
| 136 | createPayment | write createPayment plan/apply | registry-backed/live-unverified/scaffold-limited |
| 137 | createPlaceholderClientInvoice | write createPlaceholderClientInvoice plan/apply | registry-backed/live-unverified/scaffold-limited |
| 138 | createProgressInvoicingSchedule | write createProgressInvoicingSchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
| 139 | createThirdPartyPayment | write createThirdPartyPayment plan/apply | registry-backed/live-unverified/scaffold-limited |
| 140 | createTwilio10dlcA2pRegistration | write createTwilio10dlcA2pRegistration plan/apply | registry-backed/live-unverified/scaffold-limited |
| 141 | crewAddMember | write crewAddMember plan/apply | registry-backed/live-unverified/scaffold-limited |
| 142 | crewCreate | write crewCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 143 | crewDelete | write crewDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 144 | crewRemoveMember | write crewRemoveMember plan/apply | registry-backed/live-unverified/scaffold-limited |
| 145 | crewRename | write crewRename plan/apply | registry-backed/live-unverified/scaffold-limited |
| 146 | ctaConvert | write ctaConvert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 147 | ctaDismiss | write ctaDismiss plan/apply | registry-backed/live-unverified/scaffold-limited |
| 148 | ctaShown | write ctaShown plan/apply | registry-backed/live-unverified/scaffold-limited |
| 149 | customFieldConfigurationArchive | write customFieldConfigurationArchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 150 | customFieldConfigurationCreateArea | write customFieldConfigurationCreateArea plan/apply | registry-backed/live-unverified/scaffold-limited |
| 151 | customFieldConfigurationCreateDropdown | write customFieldConfigurationCreateDropdown plan/apply | registry-backed/live-unverified/scaffold-limited |
| 152 | customFieldConfigurationCreateLink | write customFieldConfigurationCreateLink plan/apply | registry-backed/live-unverified/scaffold-limited |
| 153 | customFieldConfigurationCreateNumeric | write customFieldConfigurationCreateNumeric plan/apply | registry-backed/live-unverified/scaffold-limited |
| 154 | customFieldConfigurationCreateText | write customFieldConfigurationCreateText plan/apply | registry-backed/live-unverified/scaffold-limited |
| 155 | customFieldConfigurationCreateTrueFalse | write customFieldConfigurationCreateTrueFalse plan/apply | registry-backed/live-unverified/scaffold-limited |
| 156 | customFieldConfigurationEdit | write customFieldConfigurationEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 157 | customFieldConfigurationUnarchive | write customFieldConfigurationUnarchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 158 | customLeadSourceCreate | write customLeadSourceCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 159 | customLeadSourceDelete | write customLeadSourceDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 160 | customLeadSourceEdit | write customLeadSourceEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 161 | deactivateUser | write deactivateUser plan/apply | registry-backed/live-unverified/scaffold-limited |
| 162 | deactivateUsers | write deactivateUsers plan/apply | registry-backed/live-unverified/scaffold-limited |
| 163 | deleteUser | write deleteUser plan/apply | registry-backed/live-unverified/scaffold-limited |
| 164 | deleteWorkItem | write deleteWorkItem plan/apply | registry-backed/live-unverified/scaffold-limited |
| 165 | destroyProgressInvoicingSchedule | write destroyProgressInvoicingSchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
| 166 | directUploadBeginModeration | write directUploadBeginModeration plan/apply | registry-backed/live-unverified/scaffold-limited |
| 167 | directUploadComplete | write directUploadComplete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 168 | directUploadCreate | write directUploadCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 169 | dismissCapitalCallout | write dismissCapitalCallout plan/apply | registry-backed/live-unverified/scaffold-limited |
| 170 | dismissCapitalLoanOffer | write dismissCapitalLoanOffer plan/apply | registry-backed/live-unverified/scaffold-limited |
| 171 | dismissCapitalProduct | write dismissCapitalProduct plan/apply | registry-backed/live-unverified/scaffold-limited |
| 172 | disputeClose | write disputeClose plan/apply | registry-backed/live-unverified/scaffold-limited |
| 173 | disputeEdit | write disputeEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 174 | editAppointment | write editAppointment plan/apply | registry-backed/live-unverified/scaffold-limited |
| 175 | editProgressInvoicingSchedule | write editProgressInvoicingSchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
| 176 | enableTwoFactorAuthentication | write enableTwoFactorAuthentication plan/apply | registry-backed/live-unverified/scaffold-limited |
| 177 | enrolAndRedeemPromotion | write enrolAndRedeemPromotion plan/apply | registry-backed/live-unverified/scaffold-limited |
| 178 | enrolSelfServeDowngradeSavePromo | write enrolSelfServeDowngradeSavePromo plan/apply | registry-backed/live-unverified/scaffold-limited |
| 179 | eventCreate | write eventCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 180 | eventDelete | write eventDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 181 | eventEdit | write eventEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 182 | expenseCreate | write expenseCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 183 | expenseDelete | write expenseDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 184 | expenseEdit | write expenseEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 185 | expenseUploadClose | write expenseUploadClose plan/apply | registry-backed/live-unverified/scaffold-limited |
| 186 | expenseUploadCreate | write expenseUploadCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 187 | expenseUploadDocumentConvert | write expenseUploadDocumentConvert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 188 | expenseUploadDocumentDiscard | write expenseUploadDocumentDiscard plan/apply | registry-backed/live-unverified/scaffold-limited |
| 189 | expenseUploadDocumentRetry | write expenseUploadDocumentRetry plan/apply | registry-backed/live-unverified/scaffold-limited |
| 190 | featureTrialCreate | write featureTrialCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 191 | featureTrialUpdate | write featureTrialUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 192 | findPhoneNumbers | write findPhoneNumbers plan/apply | registry-backed/live-unverified/scaffold-limited |
| 193 | franchiseCreateAccessToken | write franchiseCreateAccessToken plan/apply | registry-backed/live-unverified/scaffold-limited |
| 194 | franchiseDeleteAccessToken | write franchiseDeleteAccessToken plan/apply | registry-backed/live-unverified/scaffold-limited |
| 195 | generateAltText | write generateAltText plan/apply | registry-backed/live-unverified/scaffold-limited |
| 196 | generateMonthlyCalendar | write generateMonthlyCalendar plan/apply | registry-backed/live-unverified/scaffold-limited |
| 197 | generateOutboundCall | write generateOutboundCall plan/apply | registry-backed/live-unverified/scaffold-limited |
| 198 | globalMessageDismiss | write globalMessageDismiss plan/apply | registry-backed/live-unverified/scaffold-limited |
| 199 | googleBusinessAccountDisconnect | write googleBusinessAccountDisconnect plan/apply | registry-backed/live-unverified/scaffold-limited |
| 200 | googleBusinessAccountEdit | write googleBusinessAccountEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 201 | homeFtuxCreate | write homeFtuxCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 202 | homeFtuxRecommendationUpdate | write homeFtuxRecommendationUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 203 | importCancel | write importCancel plan/apply | registry-backed/live-unverified/scaffold-limited |
| 204 | importCreate | write importCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 205 | importRevert | write importRevert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 206 | importWorkItems | write importWorkItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 207 | inContextRecommendationDisable | write inContextRecommendationDisable plan/apply | registry-backed/live-unverified/scaffold-limited |
| 208 | intercomConversationCreate | write intercomConversationCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 209 | invoiceClose | write invoiceClose plan/apply | registry-backed/live-unverified/scaffold-limited |
| 210 | invoiceCollectSignature | write invoiceCollectSignature plan/apply | registry-backed/live-unverified/scaffold-limited |
| 211 | invoiceCreate | write invoiceCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 212 | invoiceCreateFromJob | write invoiceCreateFromJob plan/apply | registry-backed/live-unverified/scaffold-limited |
| 213 | invoiceCreateFromQuote | write invoiceCreateFromQuote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 214 | invoiceCreateFromVisits | write invoiceCreateFromVisits plan/apply | registry-backed/live-unverified/scaffold-limited |
| 215 | invoiceCreateLineItems | write invoiceCreateLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 216 | invoiceCreateNote | write invoiceCreateNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 217 | invoiceCreateNoteWaypoint | write invoiceCreateNoteWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 218 | invoiceCreatePaymentRecord | write invoiceCreatePaymentRecord plan/apply | registry-backed/live-unverified/scaffold-limited |
| 219 | invoiceDelete | write invoiceDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 220 | invoiceDeleteLineItems | write invoiceDeleteLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 221 | invoiceDeleteNote | write invoiceDeleteNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 222 | invoiceEdit | write invoiceEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 223 | invoiceEditLineItems | write invoiceEditLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 224 | invoiceEditNote | write invoiceEditNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 225 | invoiceEditTotals | write invoiceEditTotals plan/apply | registry-backed/live-unverified/scaffold-limited |
| 226 | invoiceMarkAsSent | write invoiceMarkAsSent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 227 | invoicePushToQuickBooks | write invoicePushToQuickBooks plan/apply | registry-backed/live-unverified/scaffold-limited |
| 228 | invoiceReminderCreate | write invoiceReminderCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 229 | invoiceReminderDelete | write invoiceReminderDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 230 | invoiceReminderEdit | write invoiceReminderEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 231 | invoiceRemoveTaxRate | write invoiceRemoveTaxRate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 232 | invoiceReopen | write invoiceReopen plan/apply | registry-backed/live-unverified/scaffold-limited |
| 233 | invoiceReportExportCsv | write invoiceReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 234 | invoiceUnmarkBadDebt | write invoiceUnmarkBadDebt plan/apply | registry-backed/live-unverified/scaffold-limited |
| 235 | jobClose | write jobClose plan/apply | registry-backed/live-unverified/scaffold-limited |
| 236 | jobCollectSignature | write jobCollectSignature plan/apply | registry-backed/live-unverified/scaffold-limited |
| 237 | jobCreate | write jobCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 238 | jobCreateFromQuote | write jobCreateFromQuote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 239 | jobCreateJobCosting | write jobCreateJobCosting plan/apply | registry-backed/live-unverified/scaffold-limited |
| 240 | jobCreateLineItems | write jobCreateLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 241 | jobCreateNote | write jobCreateNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 242 | jobCreateNoteWaypoint | write jobCreateNoteWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 243 | jobDelete | write jobDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 244 | jobDeleteLineItems | write jobDeleteLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 245 | jobDeleteNote | write jobDeleteNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 246 | jobEdit | write jobEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 247 | jobEditJobForms | write jobEditJobForms plan/apply | registry-backed/live-unverified/scaffold-limited |
| 248 | jobEditLineItems | write jobEditLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 249 | jobEditLineItemsSection | write jobEditLineItemsSection plan/apply | registry-backed/live-unverified/scaffold-limited |
| 250 | jobEditNote | write jobEditNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 251 | jobExportCsv | write jobExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 252 | jobExternalTransactionLink | write jobExternalTransactionLink plan/apply | registry-backed/live-unverified/scaffold-limited |
| 253 | jobExternalTransactionLinkBulk | write jobExternalTransactionLinkBulk plan/apply | registry-backed/live-unverified/scaffold-limited |
| 254 | jobFollowUpSurveySendEmail | write jobFollowUpSurveySendEmail plan/apply | registry-backed/live-unverified/scaffold-limited |
| 255 | jobFormCreate | write jobFormCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 256 | jobFormDelete | write jobFormDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 257 | jobFormEdit | write jobFormEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 258 | jobFormReportExportCsv | write jobFormReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 259 | jobNoteAddAttachment | write jobNoteAddAttachment plan/apply | registry-backed/live-unverified/scaffold-limited |
| 260 | jobOrderLineItems | write jobOrderLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 261 | jobReopen | write jobReopen plan/apply | registry-backed/live-unverified/scaffold-limited |
| 262 | jobShowcaseCreate | write jobShowcaseCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 263 | jobberPaymentsCreateRefunds | write jobberPaymentsCreateRefunds plan/apply | registry-backed/live-unverified/scaffold-limited |
| 264 | jobberPaymentsDataSharingConsentUpsert | write jobberPaymentsDataSharingConsentUpsert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 265 | jobberPaymentsEnabledStatusUpdate | write jobberPaymentsEnabledStatusUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 266 | jobberPaymentsIosTapToPayConsent | write jobberPaymentsIosTapToPayConsent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 267 | jobberPaymentsLimitsChangeRequestCancel | write jobberPaymentsLimitsChangeRequestCancel plan/apply | registry-backed/live-unverified/scaffold-limited |
| 268 | jobberPaymentsLimitsChangeRequestCreate | write jobberPaymentsLimitsChangeRequestCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 269 | jobberPaymentsManualConnectBankAccount | write jobberPaymentsManualConnectBankAccount plan/apply | registry-backed/live-unverified/scaffold-limited |
| 270 | jobberPaymentsPaymentMethodCreate | write jobberPaymentsPaymentMethodCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 271 | jobberPaymentsSetupStripeOnboarding | write jobberPaymentsSetupStripeOnboarding plan/apply | registry-backed/live-unverified/scaffold-limited |
| 272 | jobberPaymentsSurchargingConsent | write jobberPaymentsSurchargingConsent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 273 | jobberPaymentsUpdateDefaultPaymentPreference | write jobberPaymentsUpdateDefaultPaymentPreference plan/apply | registry-backed/live-unverified/scaffold-limited |
| 274 | jobsBackfillArrivalWindows | write jobsBackfillArrivalWindows plan/apply | registry-backed/live-unverified/scaffold-limited |
| 275 | jobsImport | write jobsImport plan/apply | registry-backed/live-unverified/scaffold-limited |
| 276 | jobsImportRevert | write jobsImportRevert plan/apply | registry-backed/live-unverified/scaffold-limited |
| 277 | leadSourceReportExportCsv | write leadSourceReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 278 | leadSourceSummaryReportExportCsv | write leadSourceSummaryReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 279 | locationTimersSettingsEdit | write locationTimersSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 280 | markDemoCampaignAutomationActive | write markDemoCampaignAutomationActive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 281 | markDemoCampaignSent | write markDemoCampaignSent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 282 | markMentionRead | write markMentionRead plan/apply | registry-backed/live-unverified/scaffold-limited |
| 283 | markReferralInvitationAccepted | write markReferralInvitationAccepted plan/apply | registry-backed/live-unverified/scaffold-limited |
| 284 | marketingClientReferralsSettingsEdit | write marketingClientReferralsSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 285 | marketingItemCreate | write marketingItemCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 286 | marketingItemDraftCreate | write marketingItemDraftCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 287 | marketingItemEditDate | write marketingItemEditDate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 288 | marketingItemMarkAsFailed | write marketingItemMarkAsFailed plan/apply | registry-backed/live-unverified/scaffold-limited |
| 289 | marketingItemMarkAsSent | write marketingItemMarkAsSent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 290 | marketingItemReject | write marketingItemReject plan/apply | registry-backed/live-unverified/scaffold-limited |
| 291 | marketingReviewsActivate | write marketingReviewsActivate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 292 | marketingReviewsDeactivate | write marketingReviewsDeactivate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 293 | marketingStrategyActionApprove | write marketingStrategyActionApprove plan/apply | registry-backed/live-unverified/scaffold-limited |
| 294 | marketingStrategyFeedbackCreate | write marketingStrategyFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 295 | marketingStrategyPlanRegenerate | write marketingStrategyPlanRegenerate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 296 | marketingStrategyPreviewContentOpportunityPersist | write marketingStrategyPreviewContentOpportunityPersist plan/apply | registry-backed/live-unverified/scaffold-limited |
| 297 | marketingUpdateChannelProfile | write marketingUpdateChannelProfile plan/apply | registry-backed/live-unverified/scaffold-limited |
| 298 | microSurveyFeedbackCreate | write microSurveyFeedbackCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 299 | migrateLegacyQuickbooksOnlineIntegration | write migrateLegacyQuickbooksOnlineIntegration plan/apply | registry-backed/live-unverified/scaffold-limited |
| 300 | mobileLogoutEvent | write mobileLogoutEvent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 301 | moneyManagementAccountUpdate | write moneyManagementAccountUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 302 | moneyManagementCardActivate | write moneyManagementCardActivate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 303 | moneyManagementCardUpdate | write moneyManagementCardUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 304 | moneyManagementCreateAccount | write moneyManagementCreateAccount plan/apply | registry-backed/live-unverified/scaffold-limited |
| 305 | moneyManagementCreateCardHolderAndIssueCard | write moneyManagementCreateCardHolderAndIssueCard plan/apply | registry-backed/live-unverified/scaffold-limited |
| 306 | moneyManagementCreateStripeSetupIntent | write moneyManagementCreateStripeSetupIntent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 307 | moneyManagementFetchLatestAccount | write moneyManagementFetchLatestAccount plan/apply | registry-backed/live-unverified/scaffold-limited |
| 308 | moneyManagementInitiateOutboundTransfer | write moneyManagementInitiateOutboundTransfer plan/apply | registry-backed/live-unverified/scaffold-limited |
| 309 | moneyManagementLinkVerificationDocuments | write moneyManagementLinkVerificationDocuments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 310 | moneyManagementReportsAccountStatementExportCsv | write moneyManagementReportsAccountStatementExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 311 | moneyManagementSavePaymentMethod | write moneyManagementSavePaymentMethod plan/apply | registry-backed/live-unverified/scaffold-limited |
| 312 | moneyManagementSetupStripeOnboarding | write moneyManagementSetupStripeOnboarding plan/apply | registry-backed/live-unverified/scaffold-limited |
| 313 | moneyManagementSplitValueSave | write moneyManagementSplitValueSave plan/apply | registry-backed/live-unverified/scaffold-limited |
| 314 | moneyManagementUpdateCardStatus | write moneyManagementUpdateCardStatus plan/apply | registry-backed/live-unverified/scaffold-limited |
| 315 | moneyManagementValidateTwoFactorAuthentication | write moneyManagementValidateTwoFactorAuthentication plan/apply | registry-backed/live-unverified/scaffold-limited |
| 316 | noteFilesBatchExport | write noteFilesBatchExport plan/apply | registry-backed/live-unverified/scaffold-limited |
| 317 | onMyWayTrackingLinkCreate | write onMyWayTrackingLinkCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 318 | onMyWayTrackingLinkMetadataEdit | write onMyWayTrackingLinkMetadataEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 319 | onboardingExperienceFlagUpdate | write onboardingExperienceFlagUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 320 | oneOffJobReportExportCsv | write oneOffJobReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 321 | onlineBookingConfigurationEdit | write onlineBookingConfigurationEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 322 | onlineBookingGoogleSettingsEdit | write onlineBookingGoogleSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 323 | onlineBookingMigrateToRequestForm | write onlineBookingMigrateToRequestForm plan/apply | registry-backed/live-unverified/scaffold-limited |
| 324 | onlineBookingScheduleSettingsEdit | write onlineBookingScheduleSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 325 | onlineBookingServiceAreaCreate | write onlineBookingServiceAreaCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 326 | onlineBookingServiceAreaDelete | write onlineBookingServiceAreaDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 327 | onlineBookingServiceAreaEdit | write onlineBookingServiceAreaEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 328 | onlineBookingServiceDisable | write onlineBookingServiceDisable plan/apply | registry-backed/live-unverified/scaffold-limited |
| 329 | onlineBookingServiceSortOrder | write onlineBookingServiceSortOrder plan/apply | registry-backed/live-unverified/scaffold-limited |
| 330 | onlineBookingSettingsInitialize | write onlineBookingSettingsInitialize plan/apply | registry-backed/live-unverified/scaffold-limited |
| 331 | optimizeRoute | write optimizeRoute plan/apply | registry-backed/live-unverified/scaffold-limited |
| 332 | paymentCancel | write paymentCancel plan/apply | registry-backed/live-unverified/scaffold-limited |
| 333 | paymentCapture | write paymentCapture plan/apply | registry-backed/live-unverified/scaffold-limited |
| 334 | paymentMethodCreate | write paymentMethodCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 335 | paymentMethodDelete | write paymentMethodDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 336 | paymentMethodSetAsDefault | write paymentMethodSetAsDefault plan/apply | registry-backed/live-unverified/scaffold-limited |
| 337 | paymentMethodSetupIntentCreate | write paymentMethodSetupIntentCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 338 | paymentRecordDelete | write paymentRecordDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 339 | paymentRecordEdit | write paymentRecordEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 340 | paymentTermCreate | write paymentTermCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 341 | paymentTermDelete | write paymentTermDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 342 | paymentTermEdit | write paymentTermEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 343 | payoutsExportCsv | write payoutsExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 344 | pdfSettingsUpdate | write pdfSettingsUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 345 | pipelineCardInsightsTrigger | write pipelineCardInsightsTrigger plan/apply | registry-backed/live-unverified/scaffold-limited |
| 346 | pipelineInsightsRegenerate | write pipelineInsightsRegenerate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 347 | pipelineTaskRecommendationUpdate | write pipelineTaskRecommendationUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 348 | pipelineTasksRegenerate | write pipelineTasksRegenerate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 349 | productsAndServicesCreate | write productsAndServicesCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 350 | productsAndServicesCreateFromCatalogItem | write productsAndServicesCreateFromCatalogItem plan/apply | registry-backed/live-unverified/scaffold-limited |
| 351 | productsAndServicesCreateNote | write productsAndServicesCreateNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 352 | productsAndServicesDelete | write productsAndServicesDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 353 | productsAndServicesDeleteNote | write productsAndServicesDeleteNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 354 | productsAndServicesEdit | write productsAndServicesEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 355 | productsAndServicesEditNote | write productsAndServicesEditNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 356 | productsAndServicesSyncFromCatalogItem | write productsAndServicesSyncFromCatalogItem plan/apply | registry-backed/live-unverified/scaffold-limited |
| 357 | progressInvoicingScheduleDelete | write progressInvoicingScheduleDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 358 | propertyCreate | write propertyCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 359 | propertyDelete | write propertyDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 360 | propertyEdit | write propertyEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 361 | propertyMergeCreate | write propertyMergeCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 362 | purchaseDedicatedPhoneNumber | write purchaseDedicatedPhoneNumber plan/apply | registry-backed/live-unverified/scaffold-limited |
| 363 | quoteApprove | write quoteApprove plan/apply | registry-backed/live-unverified/scaffold-limited |
| 364 | quoteArchive | write quoteArchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 365 | quoteAutoDraftFromRequest | write quoteAutoDraftFromRequest plan/apply | registry-backed/live-unverified/scaffold-limited |
| 366 | quoteCollectSignature | write quoteCollectSignature plan/apply | registry-backed/live-unverified/scaffold-limited |
| 367 | quoteCreate | write quoteCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 368 | quoteCreateAttachments | write quoteCreateAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 369 | quoteCreateImages | write quoteCreateImages plan/apply | registry-backed/live-unverified/scaffold-limited |
| 370 | quoteCreateLineItems | write quoteCreateLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 371 | quoteCreateNote | write quoteCreateNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 372 | quoteCreateNoteWaypoint | write quoteCreateNoteWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 373 | quoteCreatePaymentRecord | write quoteCreatePaymentRecord plan/apply | registry-backed/live-unverified/scaffold-limited |
| 374 | quoteCreateReviews | write quoteCreateReviews plan/apply | registry-backed/live-unverified/scaffold-limited |
| 375 | quoteCreateTextLineItems | write quoteCreateTextLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 376 | quoteDelete | write quoteDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 377 | quoteDeleteAttachments | write quoteDeleteAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 378 | quoteDeleteImages | write quoteDeleteImages plan/apply | registry-backed/live-unverified/scaffold-limited |
| 379 | quoteDeleteLineItems | write quoteDeleteLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 380 | quoteDeleteNote | write quoteDeleteNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 381 | quoteDeleteReviews | write quoteDeleteReviews plan/apply | registry-backed/live-unverified/scaffold-limited |
| 382 | quoteEdit | write quoteEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 383 | quoteEditAttachments | write quoteEditAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 384 | quoteEditImages | write quoteEditImages plan/apply | registry-backed/live-unverified/scaffold-limited |
| 385 | quoteEditLineItems | write quoteEditLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 386 | quoteEditNote | write quoteEditNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 387 | quoteEditReviews | write quoteEditReviews plan/apply | registry-backed/live-unverified/scaffold-limited |
| 388 | quoteEditTotals | write quoteEditTotals plan/apply | registry-backed/live-unverified/scaffold-limited |
| 389 | quoteIntroductionCreate | write quoteIntroductionCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 390 | quoteIntroductionDelete | write quoteIntroductionDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 391 | quoteIntroductionEdit | write quoteIntroductionEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 392 | quoteReminderComplete | write quoteReminderComplete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 393 | quoteReminderDelete | write quoteReminderDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 394 | quoteReminderEdit | write quoteReminderEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 395 | quoteReminderUncomplete | write quoteReminderUncomplete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 396 | quoteRemoveTaxRate | write quoteRemoveTaxRate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 397 | quoteReportExportCsv | write quoteReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 398 | quoteTemplateCreate | write quoteTemplateCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 399 | quoteTemplateCreateAttachments | write quoteTemplateCreateAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 400 | quoteTemplateCreateImages | write quoteTemplateCreateImages plan/apply | registry-backed/live-unverified/scaffold-limited |
| 401 | quoteTemplateCreateIntroduction | write quoteTemplateCreateIntroduction plan/apply | registry-backed/live-unverified/scaffold-limited |
| 402 | quoteTemplateCreateReviews | write quoteTemplateCreateReviews plan/apply | registry-backed/live-unverified/scaffold-limited |
| 403 | quoteTemplateDeleteAttachments | write quoteTemplateDeleteAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 404 | quoteTemplateDeleteImages | write quoteTemplateDeleteImages plan/apply | registry-backed/live-unverified/scaffold-limited |
| 405 | quoteTemplateDeleteIntroduction | write quoteTemplateDeleteIntroduction plan/apply | registry-backed/live-unverified/scaffold-limited |
| 406 | quoteTemplateDeleteReviews | write quoteTemplateDeleteReviews plan/apply | registry-backed/live-unverified/scaffold-limited |
| 407 | quoteTemplateEdit | write quoteTemplateEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 408 | quoteTemplateEditAttachments | write quoteTemplateEditAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 409 | quoteTemplateEditImages | write quoteTemplateEditImages plan/apply | registry-backed/live-unverified/scaffold-limited |
| 410 | quoteTemplateEditIntroduction | write quoteTemplateEditIntroduction plan/apply | registry-backed/live-unverified/scaffold-limited |
| 411 | quoteTemplateEditReviews | write quoteTemplateEditReviews plan/apply | registry-backed/live-unverified/scaffold-limited |
| 412 | quoteTemplateEditTotals | write quoteTemplateEditTotals plan/apply | registry-backed/live-unverified/scaffold-limited |
| 413 | quoteTemplateSyncFromCatalogItems | write quoteTemplateSyncFromCatalogItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 414 | quoteTemplatesDelete | write quoteTemplatesDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 415 | quotesArchive | write quotesArchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 416 | quotesDelete | write quotesDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 417 | quotesMarkAwaitingResponse | write quotesMarkAwaitingResponse plan/apply | registry-backed/live-unverified/scaffold-limited |
| 418 | quotesUnarchive | write quotesUnarchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 419 | reactivateUser | write reactivateUser plan/apply | registry-backed/live-unverified/scaffold-limited |
| 420 | receiveAttribution | write receiveAttribution plan/apply | registry-backed/live-unverified/scaffold-limited |
| 421 | recordFirstTouchCookie | write recordFirstTouchCookie plan/apply | registry-backed/live-unverified/scaffold-limited |
| 422 | recordGaCookie | write recordGaCookie plan/apply | registry-backed/live-unverified/scaffold-limited |
| 423 | recurringJobReportExportCsv | write recurringJobReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 424 | redeemReferralCode | write redeemReferralCode plan/apply | registry-backed/live-unverified/scaffold-limited |
| 425 | reinviteUser | write reinviteUser plan/apply | registry-backed/live-unverified/scaffold-limited |
| 426 | requestArchive | write requestArchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 427 | requestCreate | write requestCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 428 | requestCreateLineItems | write requestCreateLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 429 | requestCreateNote | write requestCreateNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 430 | requestCreateNoteWaypoint | write requestCreateNoteWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 431 | requestDelete | write requestDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 432 | requestDeleteLineItems | write requestDeleteLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 433 | requestDeleteNote | write requestDeleteNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 434 | requestEdit | write requestEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 435 | requestEditJobForms | write requestEditJobForms plan/apply | registry-backed/live-unverified/scaffold-limited |
| 436 | requestEditLineItems | write requestEditLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 437 | requestEditNote | write requestEditNote plan/apply | registry-backed/live-unverified/scaffold-limited |
| 438 | requestEditSubmission | write requestEditSubmission plan/apply | registry-backed/live-unverified/scaffold-limited |
| 439 | requestEditTotals | write requestEditTotals plan/apply | registry-backed/live-unverified/scaffold-limited |
| 440 | requestReportExportCsv | write requestReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 441 | requestRespondToPendingApproval | write requestRespondToPendingApproval plan/apply | registry-backed/live-unverified/scaffold-limited |
| 442 | requestSettingsCreate | write requestSettingsCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 443 | requestSettingsDelete | write requestSettingsDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 444 | requestSettingsEdit | write requestSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 445 | requestSettingsGlobalEdit | write requestSettingsGlobalEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 446 | requestUnarchive | write requestUnarchive plan/apply | registry-backed/live-unverified/scaffold-limited |
| 447 | restartTrial | write restartTrial plan/apply | registry-backed/live-unverified/scaffold-limited |
| 448 | reviewAttributionsEdit | write reviewAttributionsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 449 | reviewBenchmarkCreate | write reviewBenchmarkCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 450 | reviewBenchmarkEdit | write reviewBenchmarkEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 451 | reviewBenchmarkLeaderboardUpdate | write reviewBenchmarkLeaderboardUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 452 | reviewReplyEdit | write reviewReplyEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 453 | reviewReplyGenerate | write reviewReplyGenerate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 454 | reviewsInitialMessageSettingsEdit | write reviewsInitialMessageSettingsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 455 | salesPipelineCardUpdate | write salesPipelineCardUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 456 | salesPipelineStageCreate | write salesPipelineStageCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 457 | salesPipelineStageDelete | write salesPipelineStageDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 458 | salesPipelineStageEdit | write salesPipelineStageEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 459 | salespersonReportExportCsv | write salespersonReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 460 | scheduledTaskMarkComplete | write scheduledTaskMarkComplete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 461 | scheduledTaskReply | write scheduledTaskReply plan/apply | registry-backed/live-unverified/scaffold-limited |
| 462 | scheduledTaskRun | write scheduledTaskRun plan/apply | registry-backed/live-unverified/scaffold-limited |
| 463 | secureDocumentAttachFiles | write secureDocumentAttachFiles plan/apply | registry-backed/live-unverified/scaffold-limited |
| 464 | sendAppDownloadSmsInvite | write sendAppDownloadSmsInvite plan/apply | registry-backed/live-unverified/scaffold-limited |
| 465 | sendBatchRequestCardOnFileEmail | write sendBatchRequestCardOnFileEmail plan/apply | registry-backed/live-unverified/scaffold-limited |
| 466 | sendConfirmationEmail | write sendConfirmationEmail plan/apply | registry-backed/live-unverified/scaffold-limited |
| 467 | sendFeatureHighlightEmail | write sendFeatureHighlightEmail plan/apply | registry-backed/live-unverified/scaffold-limited |
| 468 | sendOnMyWayMessage | write sendOnMyWayMessage plan/apply | registry-backed/live-unverified/scaffold-limited |
| 469 | sendPasswordReset | write sendPasswordReset plan/apply | registry-backed/live-unverified/scaffold-limited |
| 470 | sendRequestCardOnFileMessage | write sendRequestCardOnFileMessage plan/apply | registry-backed/live-unverified/scaffold-limited |
| 471 | sendSms | write sendSms plan/apply | registry-backed/live-unverified/scaffold-limited |
| 472 | sendVerificationCode | write sendVerificationCode plan/apply | registry-backed/live-unverified/scaffold-limited |
| 473 | sessionRiskEvent | write sessionRiskEvent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 474 | setCaptureUserEvent | write setCaptureUserEvent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 475 | setTemporaryTwoFactorPhone | write setTemporaryTwoFactorPhone plan/apply | registry-backed/live-unverified/scaffold-limited |
| 476 | setupExperienceCreate | write setupExperienceCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 477 | setupExperienceStepStatusUpdate | write setupExperienceStepStatusUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 478 | setupGuideCreate | write setupGuideCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 479 | setupGuideEdit | write setupGuideEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 480 | setupGuideRecommendationUpdate | write setupGuideRecommendationUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 481 | setupGuideStatus | write setupGuideStatus plan/apply | registry-backed/live-unverified/scaffold-limited |
| 482 | setupGuideUpdate | write setupGuideUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 483 | setupWizardEdit | write setupWizardEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 484 | smsConversationCreate | write smsConversationCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 485 | socialMediaPostCreate | write socialMediaPostCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 486 | socialMediaPostEdit | write socialMediaPostEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 487 | socialMediaPostPublish | write socialMediaPostPublish plan/apply | registry-backed/live-unverified/scaffold-limited |
| 488 | socialMediaPostSchedule | write socialMediaPostSchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
| 489 | statementCreate | write statementCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 490 | submitVerificationCode | write submitVerificationCode plan/apply | registry-backed/live-unverified/scaffold-limited |
| 491 | subscriptionAddonCancel | write subscriptionAddonCancel plan/apply | registry-backed/live-unverified/scaffold-limited |
| 492 | subscriptionAddonRemove | write subscriptionAddonRemove plan/apply | registry-backed/live-unverified/scaffold-limited |
| 493 | subscriptionAddonsAdd | write subscriptionAddonsAdd plan/apply | registry-backed/live-unverified/scaffold-limited |
| 494 | subscriptionCancel | write subscriptionCancel plan/apply | registry-backed/live-unverified/scaffold-limited |
| 495 | subscriptionEndPause | write subscriptionEndPause plan/apply | registry-backed/live-unverified/scaffold-limited |
| 496 | subscriptionPendingChangeCancel | write subscriptionPendingChangeCancel plan/apply | registry-backed/live-unverified/scaffold-limited |
| 497 | subscriptionSchedulePause | write subscriptionSchedulePause plan/apply | registry-backed/live-unverified/scaffold-limited |
| 498 | subscriptionTermRenewalOptIn | write subscriptionTermRenewalOptIn plan/apply | registry-backed/live-unverified/scaffold-limited |
| 499 | subscriptionTermRenewalOptOut | write subscriptionTermRenewalOptOut plan/apply | registry-backed/live-unverified/scaffold-limited |
| 500 | subscriptionUpdate | write subscriptionUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 501 | supplierInvoiceDocumentRetry | write supplierInvoiceDocumentRetry plan/apply | registry-backed/live-unverified/scaffold-limited |
| 502 | supplierInvoiceDocumentsCreateExpenses | write supplierInvoiceDocumentsCreateExpenses plan/apply | registry-backed/live-unverified/scaffold-limited |
| 503 | supplierInvoiceUpload | write supplierInvoiceUpload plan/apply | registry-backed/live-unverified/scaffold-limited |
| 504 | taskCreate | write taskCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 505 | taskCreateWaypoint | write taskCreateWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 506 | taskDelete | write taskDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 507 | taskEdit | write taskEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 508 | taskEditCompleteness | write taskEditCompleteness plan/apply | registry-backed/live-unverified/scaffold-limited |
| 509 | taxCreate | write taxCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 510 | taxGroupCreate | write taxGroupCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 511 | teamProductivityReportExportCsv | write teamProductivityReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 512 | timeSheetClockIn | write timeSheetClockIn plan/apply | registry-backed/live-unverified/scaffold-limited |
| 513 | timeSheetClockOut | write timeSheetClockOut plan/apply | registry-backed/live-unverified/scaffold-limited |
| 514 | timeSheetEntryCreate | write timeSheetEntryCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 515 | timeSheetEntryCreateWaypoint | write timeSheetEntryCreateWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 516 | timeSheetEntryDelete | write timeSheetEntryDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 517 | timeSheetEntryEdit | write timeSheetEntryEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 518 | timeSheetEntryStartFromConfiguration | write timeSheetEntryStartFromConfiguration plan/apply | registry-backed/live-unverified/scaffold-limited |
| 519 | toggleFeature | write toggleFeature plan/apply | registry-backed/live-unverified/scaffold-limited |
| 520 | toggleProgressInvoicingScheduleOnJob | write toggleProgressInvoicingScheduleOnJob plan/apply | registry-backed/live-unverified/scaffold-limited |
| 521 | toggleSchedulingAvailability | write toggleSchedulingAvailability plan/apply | registry-backed/live-unverified/scaffold-limited |
| 522 | trackCapitalLoanOfferAcceptance | write trackCapitalLoanOfferAcceptance plan/apply | registry-backed/live-unverified/scaffold-limited |
| 523 | trackCapitalLoanOfferInitiated | write trackCapitalLoanOfferInitiated plan/apply | registry-backed/live-unverified/scaffold-limited |
| 524 | trackFeatureUpgrade | write trackFeatureUpgrade plan/apply | registry-backed/live-unverified/scaffold-limited |
| 525 | trackServiceProviderResponse | write trackServiceProviderResponse plan/apply | registry-backed/live-unverified/scaffold-limited |
| 526 | transferOwnership | write transferOwnership plan/apply | registry-backed/live-unverified/scaffold-limited |
| 527 | updateActivityFeedSettings | write updateActivityFeedSettings plan/apply | registry-backed/live-unverified/scaffold-limited |
| 528 | updateCalendarDisplaySettings | write updateCalendarDisplaySettings plan/apply | registry-backed/live-unverified/scaffold-limited |
| 529 | updateCompanySchedule | write updateCompanySchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
| 530 | updateFutureVisits | write updateFutureVisits plan/apply | registry-backed/live-unverified/scaffold-limited |
| 531 | updateJobCostingSettings | write updateJobCostingSettings plan/apply | registry-backed/live-unverified/scaffold-limited |
| 532 | updateJobberPaymentsManagedAccountCachedData | write updateJobberPaymentsManagedAccountCachedData plan/apply | registry-backed/live-unverified/scaffold-limited |
| 533 | updateJobberPaymentsSettings | write updateJobberPaymentsSettings plan/apply | registry-backed/live-unverified/scaffold-limited |
| 534 | updateMobileBillingInfo | write updateMobileBillingInfo plan/apply | registry-backed/live-unverified/scaffold-limited |
| 535 | updateMobilePurchase | write updateMobilePurchase plan/apply | registry-backed/live-unverified/scaffold-limited |
| 536 | updateNotification | write updateNotification plan/apply | registry-backed/live-unverified/scaffold-limited |
| 537 | updateTimeSheetDisplaySettings | write updateTimeSheetDisplaySettings plan/apply | registry-backed/live-unverified/scaffold-limited |
| 538 | updateTimeSheetPayrollPeriod | write updateTimeSheetPayrollPeriod plan/apply | registry-backed/live-unverified/scaffold-limited |
| 539 | updateTimeSheetSettings | write updateTimeSheetSettings plan/apply | registry-backed/live-unverified/scaffold-limited |
| 540 | updateUserNotificationTimestamp | write updateUserNotificationTimestamp plan/apply | registry-backed/live-unverified/scaffold-limited |
| 541 | updateWisetackApplication | write updateWisetackApplication plan/apply | registry-backed/live-unverified/scaffold-limited |
| 542 | upgradeReasonsSubscriptionUpdate | write upgradeReasonsSubscriptionUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 543 | upsertClient | write upsertClient plan/apply | registry-backed/live-unverified/scaffold-limited |
| 544 | upsertUser | write upsertUser plan/apply | registry-backed/live-unverified/scaffold-limited |
| 545 | upsertWorkItem | write upsertWorkItem plan/apply | registry-backed/live-unverified/scaffold-limited |
| 546 | userBookingScheduleCreate | write userBookingScheduleCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 547 | userBookingScheduleEdit | write userBookingScheduleEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 548 | userEdit | write userEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 549 | userSessionUpdate | write userSessionUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 550 | vehicleCreate | write vehicleCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 551 | vehicleDelete | write vehicleDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 552 | vehiclesUpdate | write vehiclesUpdate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 553 | verifyEmailConfirmationToken | write verifyEmailConfirmationToken plan/apply | registry-backed/live-unverified/scaffold-limited |
| 554 | visitBulkEdit | write visitBulkEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 555 | visitComplete | write visitComplete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 556 | visitCreate | write visitCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 557 | visitCreateLineItems | write visitCreateLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 558 | visitCreateWaypoint | write visitCreateWaypoint plan/apply | registry-backed/live-unverified/scaffold-limited |
| 559 | visitDelete | write visitDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 560 | visitDeleteLineItems | write visitDeleteLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 561 | visitEdit | write visitEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 562 | visitEditAssignedUsers | write visitEditAssignedUsers plan/apply | registry-backed/live-unverified/scaffold-limited |
| 563 | visitEditFull | write visitEditFull plan/apply | registry-backed/live-unverified/scaffold-limited |
| 564 | visitEditLineItems | write visitEditLineItems plan/apply | registry-backed/live-unverified/scaffold-limited |
| 565 | visitEditSchedule | write visitEditSchedule plan/apply | registry-backed/live-unverified/scaffold-limited |
| 566 | visitFormSubmission | write visitFormSubmission plan/apply | registry-backed/live-unverified/scaffold-limited |
| 567 | visitReportExportCsv | write visitReportExportCsv plan/apply | registry-backed/live-unverified/scaffold-limited |
| 568 | visitStartTimer | write visitStartTimer plan/apply | registry-backed/live-unverified/scaffold-limited |
| 569 | visitStopTimer | write visitStopTimer plan/apply | registry-backed/live-unverified/scaffold-limited |
| 570 | visitUncomplete | write visitUncomplete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 571 | webhookEndpointCreate | write webhookEndpointCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 572 | webhookEndpointDelete | write webhookEndpointDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 573 | webhookSubscriptionCreate | write webhookSubscriptionCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 574 | webhookSubscriptionDelete | write webhookSubscriptionDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 575 | websiteAddCustomDomain | write websiteAddCustomDomain plan/apply | registry-backed/live-unverified/scaffold-limited |
| 576 | websiteCreate | write websiteCreate plan/apply | registry-backed/live-unverified/scaffold-limited |
| 577 | websiteCreatePage | write websiteCreatePage plan/apply | registry-backed/live-unverified/scaffold-limited |
| 578 | websiteCreatePageFromMarketingItem | write websiteCreatePageFromMarketingItem plan/apply | registry-backed/live-unverified/scaffold-limited |
| 579 | websiteCreatePageGroup | write websiteCreatePageGroup plan/apply | registry-backed/live-unverified/scaffold-limited |
| 580 | websiteCreatePreview | write websiteCreatePreview plan/apply | registry-backed/live-unverified/scaffold-limited |
| 581 | websiteCreateSections | write websiteCreateSections plan/apply | registry-backed/live-unverified/scaffold-limited |
| 582 | websiteDelete | write websiteDelete plan/apply | registry-backed/live-unverified/scaffold-limited |
| 583 | websiteDeletePage | write websiteDeletePage plan/apply | registry-backed/live-unverified/scaffold-limited |
| 584 | websiteDeletePageGroup | write websiteDeletePageGroup plan/apply | registry-backed/live-unverified/scaffold-limited |
| 585 | websiteEdit | write websiteEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 586 | websiteEditPageGroup | write websiteEditPageGroup plan/apply | registry-backed/live-unverified/scaffold-limited |
| 587 | websiteGenerateOnboardingContent | write websiteGenerateOnboardingContent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 588 | websiteGeneratePageContent | write websiteGeneratePageContent plan/apply | registry-backed/live-unverified/scaffold-limited |
| 589 | websiteLinkGoogleBusinessProfile | write websiteLinkGoogleBusinessProfile plan/apply | registry-backed/live-unverified/scaffold-limited |
| 590 | websiteUnlinkCustomDomain | write websiteUnlinkCustomDomain plan/apply | registry-backed/live-unverified/scaffold-limited |
| 591 | websiteUnlinkGoogleBusinessProfile | write websiteUnlinkGoogleBusinessProfile plan/apply | registry-backed/live-unverified/scaffold-limited |
| 592 | workObjectCreateEmailAttachments | write workObjectCreateEmailAttachments plan/apply | registry-backed/live-unverified/scaffold-limited |
| 593 | workObjectGlobalOwnershipsEdit | write workObjectGlobalOwnershipsEdit plan/apply | registry-backed/live-unverified/scaffold-limited |
| 594 | workObjectPreviewPdf | write workObjectPreviewPdf plan/apply | registry-backed/live-unverified/scaffold-limited |
| 595 | workObjectSendEmail | write workObjectSendEmail plan/apply | registry-backed/live-unverified/scaffold-limited |
| 596 | workObjectSendSms | write workObjectSendSms plan/apply | registry-backed/live-unverified/scaffold-limited |

## Webhook topic coverage
| # | Topic | Planned command | Status |
|---|---|---|---|
|   1 | APP_CONNECT | webhooks topics APP_CONNECT | topic-listed/live-unverified |
|   2 | APP_DISCONNECT | webhooks topics APP_DISCONNECT | topic-listed/live-unverified |
|   3 | CLIENT_CREATE | webhooks topics CLIENT_CREATE | topic-listed/live-unverified |
|   4 | CLIENT_DESTROY | webhooks topics CLIENT_DESTROY | topic-listed/live-unverified |
|   5 | CLIENT_UPDATE | webhooks topics CLIENT_UPDATE | topic-listed/live-unverified |
|   6 | INVOICE_CREATE | webhooks topics INVOICE_CREATE | topic-listed/live-unverified |
|   7 | INVOICE_DESTROY | webhooks topics INVOICE_DESTROY | topic-listed/live-unverified |
|   8 | INVOICE_UPDATE | webhooks topics INVOICE_UPDATE | topic-listed/live-unverified |
|   9 | JOB_CREATE | webhooks topics JOB_CREATE | topic-listed/live-unverified |
|  10 | JOB_DESTROY | webhooks topics JOB_DESTROY | topic-listed/live-unverified |
|  11 | JOB_UPDATE | webhooks topics JOB_UPDATE | topic-listed/live-unverified |
|  12 | JOB_CLOSED | webhooks topics JOB_CLOSED | topic-listed/live-unverified |
|  13 | PROPERTY_CREATE | webhooks topics PROPERTY_CREATE | topic-listed/live-unverified |
|  14 | PROPERTY_DESTROY | webhooks topics PROPERTY_DESTROY | topic-listed/live-unverified |
|  15 | PROPERTY_UPDATE | webhooks topics PROPERTY_UPDATE | topic-listed/live-unverified |
|  16 | QUOTE_CREATE | webhooks topics QUOTE_CREATE | topic-listed/live-unverified |
|  17 | QUOTE_DESTROY | webhooks topics QUOTE_DESTROY | topic-listed/live-unverified |
|  18 | QUOTE_UPDATE | webhooks topics QUOTE_UPDATE | topic-listed/live-unverified |
|  19 | QUOTE_SENT | webhooks topics QUOTE_SENT | topic-listed/live-unverified |
|  20 | QUOTE_APPROVED | webhooks topics QUOTE_APPROVED | topic-listed/live-unverified |
|  21 | REQUEST_CREATE | webhooks topics REQUEST_CREATE | topic-listed/live-unverified |
|  22 | REQUEST_DESTROY | webhooks topics REQUEST_DESTROY | topic-listed/live-unverified |
|  23 | REQUEST_UPDATE | webhooks topics REQUEST_UPDATE | topic-listed/live-unverified |
|  24 | VISIT_COMPLETE | webhooks topics VISIT_COMPLETE | topic-listed/live-unverified |
|  25 | VISIT_CREATE | webhooks topics VISIT_CREATE | topic-listed/live-unverified |
|  26 | VISIT_DESTROY | webhooks topics VISIT_DESTROY | topic-listed/live-unverified |
|  27 | VISIT_UPDATE | webhooks topics VISIT_UPDATE | topic-listed/live-unverified |
|  28 | PRODUCT_OR_SERVICE_CREATE | webhooks topics PRODUCT_OR_SERVICE_CREATE | topic-listed/live-unverified |
|  29 | PRODUCT_OR_SERVICE_DESTROY | webhooks topics PRODUCT_OR_SERVICE_DESTROY | topic-listed/live-unverified |
|  30 | PRODUCT_OR_SERVICE_UPDATE | webhooks topics PRODUCT_OR_SERVICE_UPDATE | topic-listed/live-unverified |
|  31 | PAYMENT_CREATE | webhooks topics PAYMENT_CREATE | topic-listed/live-unverified |
|  32 | PAYMENT_DESTROY | webhooks topics PAYMENT_DESTROY | topic-listed/live-unverified |
|  33 | PAYMENT_UPDATE | webhooks topics PAYMENT_UPDATE | topic-listed/live-unverified |
|  34 | PAYOUT_CREATE | webhooks topics PAYOUT_CREATE | topic-listed/live-unverified |
|  35 | PAYOUT_DESTROY | webhooks topics PAYOUT_DESTROY | topic-listed/live-unverified |
|  36 | PAYOUT_UPDATE | webhooks topics PAYOUT_UPDATE | topic-listed/live-unverified |
|  37 | TIMESHEET_CREATE | webhooks topics TIMESHEET_CREATE | topic-listed/live-unverified |
|  38 | TIMESHEET_DESTROY | webhooks topics TIMESHEET_DESTROY | topic-listed/live-unverified |
|  39 | TIMESHEET_UPDATE | webhooks topics TIMESHEET_UPDATE | topic-listed/live-unverified |
|  40 | EXPENSE_CREATE | webhooks topics EXPENSE_CREATE | topic-listed/live-unverified |
|  41 | EXPENSE_DESTROY | webhooks topics EXPENSE_DESTROY | topic-listed/live-unverified |
|  42 | EXPENSE_UPDATE | webhooks topics EXPENSE_UPDATE | topic-listed/live-unverified |
|  43 | ON_MY_WAY_TRACKING_LINK_REQUEST | webhooks topics ON_MY_WAY_TRACKING_LINK_REQUEST | topic-listed/live-unverified |
|  44 | MARKETING_ITEM_UPDATE | webhooks topics MARKETING_ITEM_UPDATE | topic-listed/live-unverified |
|  45 | USER_CREATE | webhooks topics USER_CREATE | topic-listed/live-unverified |
|  46 | USER_UPDATE | webhooks topics USER_UPDATE | topic-listed/live-unverified |

## API inventory source of truth references
- Source counts: 384 Query fields, 596 Mutation fields, 46 webhook topics.
- API schema version header source: `api_version_header: 2025-04-16`.
- Source fetched UTC date: 2026-06-11.

## Known gap list
- No operation command has been verified against a live Jobber account in this repo run.
- Webhook topics are listed and signature verification is local, but endpoint delivery is not live-verified.
- Query and mutation arguments are validated against schema argument names, but account-specific scopes, required input shapes, and business rules still require live Jobber verification.
- Mutation commands are registry-backed and plan-first; they do not yet include per-mutation before-state snapshots or operation-specific read-back verification recipes.
