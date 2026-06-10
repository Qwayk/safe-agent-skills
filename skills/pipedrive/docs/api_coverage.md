# API Coverage (main reference)

This table is built from the official Pipedrive OpenAPI specs and is used as main reference for shipped command coverage and exclusions.
Scope note: this tool is intentionally read-only by product choice, not by omission.


## Source summary
- Deduped public surface: **336** method+path pairs.
- GET rows mapped to shipped read commands: **161**.
- GET rows excluded from the shipped command surface: **1** (`/oauth/authorize`, OAuth-only auth flow).
- Non-GET rows marked excluded: **174** (`excluded by choice: read-only tool`).
- Both v1/v2 versions published: **35** rows, preferring v2 for command selection.
- Last verified sources: 2026-05-21.

| Method | Path | Preferred version | Available versions | Shipped CLI command or exclusion | Auth | Token cost | Notes |
|---|---|---|---|---|---|---|---|
| DELETE | /activities/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /activityTypes/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /boards/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /callLogs/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /channels/{channel-id}/conversations/{conversation-id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /channels/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /dealFields | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /dealFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /dealFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /dealFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id}/discounts/{discount_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id}/followers/{follower_id} | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 6 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id}/installments/{installment_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id}/participants/{deal_participant_id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id}/products | v2 | v2 | excluded by choice: read-only tool | x-api-token | 15 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /deals/{id}/products/{product_attachment_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /files/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /filters | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /filters/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /goals/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /leadLabels/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /leads/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /legacyTeams/{id}/users | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /mailbox/mailThreads/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /meetings/userProviderLinks/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /notes/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /notes/{id}/comments/{commentId} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizationFields | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizationFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizationFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizationFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizationRelationships/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizations/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /organizations/{id}/followers/{follower_id} | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 6 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /personFields | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /personFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /personFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /personFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /persons/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /persons/{id}/followers/{follower_id} | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 6 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /persons/{id}/picture | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /phases/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /pipelines/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /productFields | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /productFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /productFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /productFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /products/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /products/{id}/followers/{follower_id} | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 6 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /products/{id}/images | v2 | v2 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /products/{id}/variations/{product_variation_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /projectFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /projectFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /projects/{id} | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 6 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /roles/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /roles/{id}/assignments | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /stages/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 3 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /tasks/{id} | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 6 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| DELETE | /webhooks/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 6 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| GET | /activities | v2 | v2 | qwayk-pipedrive-safe-agent-cli activities list | x-api-token | 10 | shipped read command |
| GET | /activities/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli activities get | x-api-token | 1 | shipped read command |
| GET | /activityFields | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli activity-fields list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /activityFields/{field_code} | v2 | v2 | qwayk-pipedrive-safe-agent-cli activity-fields get | x-api-token | 1 | shipped read command |
| GET | /activityTypes | v1 | v1 | qwayk-pipedrive-safe-agent-cli activity-types list | x-api-token | 20 | shipped read command |
| GET | /billing/subscriptions/addons | v1 | v1 | qwayk-pipedrive-safe-agent-cli billing list-addons | x-api-token | 20 | shipped read command |
| GET | /boards | v2 | v2 | qwayk-pipedrive-safe-agent-cli project-boards list | x-api-token | 10 | shipped read command |
| GET | /boards/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli project-boards get | x-api-token | 10 | shipped read command |
| GET | /callLogs | v1 | v1 | qwayk-pipedrive-safe-agent-cli call-logs list | x-api-token | 20 | shipped read command |
| GET | /callLogs/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli call-logs get | x-api-token | 2 | shipped read command |
| GET | /currencies | v1 | v1 | qwayk-pipedrive-safe-agent-cli currencies list | x-api-token | 20 | shipped read command |
| GET | /dealFields | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli deal-fields list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /dealFields/{field_code} | v2 | v2 | qwayk-pipedrive-safe-agent-cli deal-fields get | x-api-token | 1 | shipped read command |
| GET | /dealFields/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli deal-fields get | x-api-token | 2 | shipped read command |
| GET | /deals | v2 | v2 | qwayk-pipedrive-safe-agent-cli deals list | x-api-token | 10 | shipped read command |
| GET | /deals/archived | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli deals list-archived | x-api-token | v1: 40 / v2: 20 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /deals/installments | v2 | v2 | qwayk-pipedrive-safe-agent-cli deal-installments list | x-api-token | 10 | shipped read command |
| GET | /deals/products | v2 | v2 | qwayk-pipedrive-safe-agent-cli deal-products list | x-api-token | 10 | shipped read command |
| GET | /deals/search | v2 | v2 | qwayk-pipedrive-safe-agent-cli deals search | x-api-token | 20 | shipped read command |
| GET | /deals/summary | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals summary | x-api-token | 40 | shipped read command |
| GET | /deals/summary/archived | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals summary-archived | x-api-token | 80 | shipped read command |
| GET | /deals/timeline | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals timeline | x-api-token | 20 | shipped read command |
| GET | /deals/timeline/archived | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals timeline-archived | x-api-token | 40 | shipped read command |
| GET | /deals/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli deals get | x-api-token | 1 | shipped read command |
| GET | /deals/{id}/changelog | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals changelog | x-api-token | 20 | shipped read command |
| GET | /deals/{id}/convert/status/{conversion_id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli deals conversion-status | x-api-token | 1 | shipped read command |
| GET | /deals/{id}/discounts | v2 | v2 | qwayk-pipedrive-safe-agent-cli deals discounts | x-api-token | 10 | shipped read command |
| GET | /deals/{id}/files | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals files | x-api-token | 20 | shipped read command |
| GET | /deals/{id}/flow | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals flow | x-api-token | 40 | shipped read command |
| GET | /deals/{id}/followers | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli deals followers | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /deals/{id}/followers/changelog | v2 | v2 | qwayk-pipedrive-safe-agent-cli deals followers-changelog | x-api-token | 10 | shipped read command |
| GET | /deals/{id}/mailMessages | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals mail-messages | x-api-token | 20 | shipped read command |
| GET | /deals/{id}/participants | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals participants | x-api-token | 10 | shipped read command |
| GET | /deals/{id}/participantsChangelog | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals participants-changelog | x-api-token | 10 | shipped read command |
| GET | /deals/{id}/permittedUsers | v1 | v1 | qwayk-pipedrive-safe-agent-cli deals permitted-users | x-api-token | 10 | shipped read command |
| GET | /deals/{id}/products | v2 | v2 | qwayk-pipedrive-safe-agent-cli deal-products list-for-deal | x-api-token | 10 | shipped read command |
| GET | /files | v1 | v1 | qwayk-pipedrive-safe-agent-cli files list | x-api-token | 20 | shipped read command |
| GET | /files/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli files get | x-api-token | 2 | shipped read command |
| GET | /files/{id}/download | v1 | v1 | qwayk-pipedrive-safe-agent-cli files download | x-api-token | 20 | Binary response endpoint. CLI must not auto-download by default. |
| GET | /filters | v1 | v1 | qwayk-pipedrive-safe-agent-cli filters list | x-api-token | 20 | shipped read command |
| GET | /filters/helpers | v1 | v1 | qwayk-pipedrive-safe-agent-cli filters helpers | x-api-token | 20 | shipped read command |
| GET | /filters/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli filters get | x-api-token | 2 | shipped read command |
| GET | /goals/find | v1 | v1 | qwayk-pipedrive-safe-agent-cli goals search | x-api-token | 20 | shipped read command |
| GET | /goals/{id}/results | v1 | v1 | qwayk-pipedrive-safe-agent-cli goals get-results | x-api-token | 20 | shipped read command |
| GET | /itemSearch | v2 | v2 | qwayk-pipedrive-safe-agent-cli item-search search | x-api-token | 20 | shipped read command |
| GET | /itemSearch/field | v2 | v2 | qwayk-pipedrive-safe-agent-cli item-search field-search | x-api-token | 20 | shipped read command |
| GET | /leadFields | v1 | v1 | qwayk-pipedrive-safe-agent-cli lead-fields list | x-api-token | 20 | shipped read command |
| GET | /leadLabels | v1 | v1 | qwayk-pipedrive-safe-agent-cli lead-labels list | x-api-token | 10 | shipped read command |
| GET | /leadSources | v1 | v1 | qwayk-pipedrive-safe-agent-cli lead-sources list | x-api-token | 2 | shipped read command |
| GET | /leads | v1 | v1 | qwayk-pipedrive-safe-agent-cli leads list | x-api-token | 20 | shipped read command |
| GET | /leads/archived | v1 | v1 | qwayk-pipedrive-safe-agent-cli leads list-archived | x-api-token | 40 | shipped read command |
| GET | /leads/search | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli leads search | x-api-token | v1: 40 / v2: 20 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /leads/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli leads get | x-api-token | 2 | shipped read command |
| GET | /leads/{id}/convert/status/{conversion_id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli leads conversion-status | x-api-token | 1 | shipped read command |
| GET | /leads/{id}/permittedUsers | v1 | v1 | qwayk-pipedrive-safe-agent-cli leads permitted-users | x-api-token | 10 | shipped read command |
| GET | /legacyTeams | v1 | v1 | qwayk-pipedrive-safe-agent-cli legacy-teams list | x-api-token | 20 | shipped read command |
| GET | /legacyTeams/user/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli legacy-teams list-for-user | x-api-token | 20 | shipped read command |
| GET | /legacyTeams/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli legacy-teams get | x-api-token | 2 | shipped read command |
| GET | /legacyTeams/{id}/users | v1 | v1 | qwayk-pipedrive-safe-agent-cli legacy-teams list-users | x-api-token | 20 | shipped read command |
| GET | /mailbox/mailMessages/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli mailbox get-message | x-api-token | 2 | shipped read command |
| GET | /mailbox/mailThreads | v1 | v1 | qwayk-pipedrive-safe-agent-cli mailbox list-threads | x-api-token | 20 | shipped read command |
| GET | /mailbox/mailThreads/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli mailbox get-thread | x-api-token | 20 | shipped read command |
| GET | /mailbox/mailThreads/{id}/mailMessages | v1 | v1 | qwayk-pipedrive-safe-agent-cli mailbox list-thread-messages | x-api-token | 20 | shipped read command |
| GET | /noteFields | v1 | v1 | qwayk-pipedrive-safe-agent-cli note-fields list | x-api-token | 20 | shipped read command |
| GET | /notes | v1 | v1 | qwayk-pipedrive-safe-agent-cli notes list | x-api-token | 20 | shipped read command |
| GET | /notes/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli notes get | x-api-token | 2 | shipped read command |
| GET | /notes/{id}/comments | v1 | v1 | qwayk-pipedrive-safe-agent-cli notes list-comments | x-api-token | 20 | shipped read command |
| GET | /notes/{id}/comments/{commentId} | v1 | v1 | qwayk-pipedrive-safe-agent-cli notes get-comment | x-api-token | 2 | shipped read command |
| GET | /oauth/authorize | v1 | v1 | excluded by choice: OAuth-only endpoint | OAuth only | 0 | OAuth-only auth flow; outside API-token read tool scope. |
| GET | /organizationFields | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli organization-fields list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /organizationFields/{field_code} | v2 | v2 | qwayk-pipedrive-safe-agent-cli organization-fields get | x-api-token | 1 | shipped read command |
| GET | /organizationFields/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli organization-fields get | x-api-token | 2 | shipped read command |
| GET | /organizationRelationships | v1 | v1 | qwayk-pipedrive-safe-agent-cli organization-relationships list | x-api-token | 20 | shipped read command |
| GET | /organizationRelationships/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli organization-relationships get | x-api-token | 2 | shipped read command |
| GET | /organizations | v2 | v2 | qwayk-pipedrive-safe-agent-cli organizations list | x-api-token | 10 | shipped read command |
| GET | /organizations/search | v2 | v2 | qwayk-pipedrive-safe-agent-cli organizations search | x-api-token | 20 | shipped read command |
| GET | /organizations/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli organizations get | x-api-token | 1 | shipped read command |
| GET | /organizations/{id}/changelog | v1 | v1 | qwayk-pipedrive-safe-agent-cli organizations changelog | x-api-token | 20 | shipped read command |
| GET | /organizations/{id}/files | v1 | v1 | qwayk-pipedrive-safe-agent-cli organizations files | x-api-token | 20 | shipped read command |
| GET | /organizations/{id}/flow | v1 | v1 | qwayk-pipedrive-safe-agent-cli organizations flow | x-api-token | 40 | shipped read command |
| GET | /organizations/{id}/followers | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli organizations followers | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /organizations/{id}/followers/changelog | v2 | v2 | qwayk-pipedrive-safe-agent-cli organizations followers-changelog | x-api-token | 10 | shipped read command |
| GET | /organizations/{id}/mailMessages | v1 | v1 | qwayk-pipedrive-safe-agent-cli organizations mail-messages | x-api-token | 20 | shipped read command |
| GET | /organizations/{id}/permittedUsers | v1 | v1 | qwayk-pipedrive-safe-agent-cli organizations permitted-users | x-api-token | 10 | shipped read command |
| GET | /permissionSets | v1 | v1 | qwayk-pipedrive-safe-agent-cli permission-sets list | x-api-token | 20 | shipped read command |
| GET | /permissionSets/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli permission-sets get | x-api-token | 2 | shipped read command |
| GET | /permissionSets/{id}/assignments | v1 | v1 | qwayk-pipedrive-safe-agent-cli permission-sets list-assignments | x-api-token | 20 | shipped read command |
| GET | /personFields | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli person-fields list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /personFields/{field_code} | v2 | v2 | qwayk-pipedrive-safe-agent-cli person-fields get | x-api-token | 1 | shipped read command |
| GET | /personFields/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli person-fields get | x-api-token | 2 | shipped read command |
| GET | /persons | v2 | v2 | qwayk-pipedrive-safe-agent-cli persons list | x-api-token | 10 | shipped read command |
| GET | /persons/search | v2 | v2 | qwayk-pipedrive-safe-agent-cli persons search | x-api-token | 20 | shipped read command |
| GET | /persons/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli persons get | x-api-token | 1 | shipped read command |
| GET | /persons/{id}/changelog | v1 | v1 | qwayk-pipedrive-safe-agent-cli persons changelog | x-api-token | 20 | shipped read command |
| GET | /persons/{id}/files | v1 | v1 | qwayk-pipedrive-safe-agent-cli persons files | x-api-token | 20 | shipped read command |
| GET | /persons/{id}/flow | v1 | v1 | qwayk-pipedrive-safe-agent-cli persons flow | x-api-token | 40 | shipped read command |
| GET | /persons/{id}/followers | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli persons followers | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /persons/{id}/followers/changelog | v2 | v2 | qwayk-pipedrive-safe-agent-cli persons followers-changelog | x-api-token | 10 | shipped read command |
| GET | /persons/{id}/mailMessages | v1 | v1 | qwayk-pipedrive-safe-agent-cli persons mail-messages | x-api-token | 20 | shipped read command |
| GET | /persons/{id}/permittedUsers | v1 | v1 | qwayk-pipedrive-safe-agent-cli persons permitted-users | x-api-token | 10 | shipped read command |
| GET | /persons/{id}/picture | v2 | v2 | qwayk-pipedrive-safe-agent-cli persons picture | x-api-token | 1 | shipped read command |
| GET | /persons/{id}/products | v1 | v1 | qwayk-pipedrive-safe-agent-cli persons list-products | x-api-token | 20 | shipped read command |
| GET | /phases | v2 | v2 | qwayk-pipedrive-safe-agent-cli project-phases list | x-api-token | 10 | shipped read command |
| GET | /phases/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli project-phases get | x-api-token | 10 | shipped read command |
| GET | /pipelines | v2 | v2 | qwayk-pipedrive-safe-agent-cli pipelines list | x-api-token | 5 | shipped read command |
| GET | /pipelines/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli pipelines get | x-api-token | 1 | shipped read command |
| GET | /pipelines/{id}/conversion_statistics | v1 | v1 | qwayk-pipedrive-safe-agent-cli pipelines conversion-statistics | x-api-token | 40 | shipped read command |
| GET | /pipelines/{id}/deals | v1 | v1 | qwayk-pipedrive-safe-agent-cli pipelines list-deals | x-api-token | 20 | shipped read command |
| GET | /pipelines/{id}/movement_statistics | v1 | v1 | qwayk-pipedrive-safe-agent-cli pipelines movement-statistics | x-api-token | 40 | shipped read command |
| GET | /productFields | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli product-fields list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /productFields/{field_code} | v2 | v2 | qwayk-pipedrive-safe-agent-cli product-fields get | x-api-token | 1 | shipped read command |
| GET | /productFields/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli product-fields get | x-api-token | 2 | shipped read command |
| GET | /products | v2 | v2 | qwayk-pipedrive-safe-agent-cli products list | x-api-token | 10 | shipped read command |
| GET | /products/search | v2 | v2 | qwayk-pipedrive-safe-agent-cli products search | x-api-token | 20 | shipped read command |
| GET | /products/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli products get | x-api-token | 1 | shipped read command |
| GET | /products/{id}/deals | v1 | v1 | qwayk-pipedrive-safe-agent-cli products list-deals | x-api-token | 20 | shipped read command |
| GET | /products/{id}/files | v1 | v1 | qwayk-pipedrive-safe-agent-cli products files | x-api-token | 20 | shipped read command |
| GET | /products/{id}/followers | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli products followers | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /products/{id}/followers/changelog | v2 | v2 | qwayk-pipedrive-safe-agent-cli products followers-changelog | x-api-token | 10 | shipped read command |
| GET | /products/{id}/images | v2 | v2 | qwayk-pipedrive-safe-agent-cli products images | x-api-token | 10 | shipped read command |
| GET | /products/{id}/permittedUsers | v1 | v1 | qwayk-pipedrive-safe-agent-cli products permitted-users | x-api-token | 10 | shipped read command |
| GET | /products/{id}/variations | v2 | v2 | qwayk-pipedrive-safe-agent-cli products variations | x-api-token | 10 | shipped read command |
| GET | /projectFields | v2 | v2 | qwayk-pipedrive-safe-agent-cli project-fields list | x-api-token | 10 | shipped read command |
| GET | /projectFields/{field_code} | v2 | v2 | qwayk-pipedrive-safe-agent-cli project-fields get | x-api-token | 1 | shipped read command |
| GET | /projectTemplates | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli project-templates list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /projectTemplates/{id} | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli project-templates get | x-api-token | v1: 2 / v2: 1 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /projects | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli projects list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /projects/archived | v2 | v2 | qwayk-pipedrive-safe-agent-cli projects list-archived | x-api-token | 10 | shipped read command |
| GET | /projects/boards | v1 | v1 | qwayk-pipedrive-safe-agent-cli project-boards list | x-api-token | 20 | shipped read command |
| GET | /projects/boards/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli project-boards get | x-api-token | 2 | shipped read command |
| GET | /projects/phases | v1 | v1 | qwayk-pipedrive-safe-agent-cli project-phases list | x-api-token | 20 | shipped read command |
| GET | /projects/phases/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli project-phases get | x-api-token | 2 | shipped read command |
| GET | /projects/search | v2 | v2 | qwayk-pipedrive-safe-agent-cli projects search | x-api-token | 20 | shipped read command |
| GET | /projects/{id} | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli projects get | x-api-token | v1: 2 / v2: 1 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /projects/{id}/activities | v1 | v1 | qwayk-pipedrive-safe-agent-cli projects list-activities | x-api-token | 20 | shipped read command |
| GET | /projects/{id}/changelog | v2 | v2 | qwayk-pipedrive-safe-agent-cli projects changelog | x-api-token | 10 | shipped read command |
| GET | /projects/{id}/groups | v1 | v1 | qwayk-pipedrive-safe-agent-cli projects list-groups | x-api-token | 20 | shipped read command |
| GET | /projects/{id}/permittedUsers | v2 | v2 | qwayk-pipedrive-safe-agent-cli projects permitted-users | x-api-token | 5 | shipped read command |
| GET | /projects/{id}/plan | v1 | v1 | qwayk-pipedrive-safe-agent-cli projects get-plan | x-api-token | 20 | shipped read command |
| GET | /projects/{id}/tasks | v1 | v1 | qwayk-pipedrive-safe-agent-cli projects list-tasks | x-api-token | 20 | shipped read command |
| GET | /recents | v1 | v1 | qwayk-pipedrive-safe-agent-cli recents list | x-api-token | 20 | shipped read command |
| GET | /roles | v1 | v1 | qwayk-pipedrive-safe-agent-cli roles list | x-api-token | 20 | shipped read command |
| GET | /roles/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli roles get | x-api-token | 2 | shipped read command |
| GET | /roles/{id}/assignments | v1 | v1 | qwayk-pipedrive-safe-agent-cli roles list-assignments | x-api-token | 10 | shipped read command |
| GET | /roles/{id}/pipelines | v1 | v1 | qwayk-pipedrive-safe-agent-cli roles list-pipeline-visibility | x-api-token | 20 | shipped read command |
| GET | /roles/{id}/settings | v1 | v1 | qwayk-pipedrive-safe-agent-cli roles list-settings | x-api-token | 20 | shipped read command |
| GET | /stages | v2 | v2 | qwayk-pipedrive-safe-agent-cli stages list | x-api-token | 5 | shipped read command |
| GET | /stages/{id} | v2 | v2 | qwayk-pipedrive-safe-agent-cli stages get | x-api-token | 1 | shipped read command |
| GET | /stages/{id}/deals | v1 | v1 | qwayk-pipedrive-safe-agent-cli stages list-deals | x-api-token | 20 | shipped read command |
| GET | /tasks | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli tasks list | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /tasks/{id} | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli tasks get | x-api-token | v1: 2 / v2: 1 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /userConnections | v1 | v1 | qwayk-pipedrive-safe-agent-cli user-connections list | x-api-token | 20 | shipped read command |
| GET | /userSettings | v1 | v1 | qwayk-pipedrive-safe-agent-cli user-settings list | x-api-token | 2 | shipped read command |
| GET | /users | v1 | v1 | qwayk-pipedrive-safe-agent-cli users list | x-api-token | 20 | shipped read command |
| GET | /users/find | v1 | v1 | qwayk-pipedrive-safe-agent-cli users search | x-api-token | 40 | shipped read command |
| GET | /users/me | v1 | v1 | qwayk-pipedrive-safe-agent-cli users get-current | x-api-token | 2 | shipped read command |
| GET | /users/{id} | v1 | v1 | qwayk-pipedrive-safe-agent-cli users get | x-api-token | 2 | shipped read command |
| GET | /users/{id}/followers | v2 | v1, v2 | qwayk-pipedrive-safe-agent-cli users followers | x-api-token | v1: 20 / v2: 10 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. |
| GET | /users/{id}/permissions | v1 | v1 | qwayk-pipedrive-safe-agent-cli users list-permissions | x-api-token | 10 | shipped read command |
| GET | /users/{id}/roleAssignments | v1 | v1 | qwayk-pipedrive-safe-agent-cli users role-assignments | x-api-token | 10 | shipped read command |
| GET | /users/{id}/roleSettings | v1 | v1 | qwayk-pipedrive-safe-agent-cli users role-settings | x-api-token | 10 | shipped read command |
| GET | /webhooks | v1 | v1 | qwayk-pipedrive-safe-agent-cli webhooks list | x-api-token | 10 | shipped read command |
| PATCH | /activities/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /boards/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /dealFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /dealFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /deals/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /deals/{id}/discounts/{discount_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /deals/{id}/installments/{installment_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /deals/{id}/products/{product_attachment_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /leadLabels/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /leads/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /organizationFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /organizationFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /organizations/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /personFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /personFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /persons/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /phases/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /pipelines/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /productFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /productFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /products/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /products/{id}/variations/{product_variation_id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /projectFields/{field_code} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /projectFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /projects/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /stages/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PATCH | /tasks/{id} | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /activities | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /activityTypes | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /boards | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /callLogs | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /callLogs/{id}/recordings | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /channels | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /channels/messages/receive | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /dealFields | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /dealFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/convert/lead | v2 | v2 | excluded by choice: read-only tool | x-api-token | 40 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/discounts | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/duplicate | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/followers | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/installments | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/participants | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/products | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /deals/{id}/products/bulk | v2 | v2 | excluded by choice: read-only tool | x-api-token | 25 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /files | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /files/remote | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /files/remoteLink | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /filters | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /goals | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /leadLabels | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /leads | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /leads/{id}/convert/deal | v2 | v2 | excluded by choice: read-only tool | x-api-token | 40 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /legacyTeams | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /legacyTeams/{id}/users | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /meetings/userProviderLinks | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /notes | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /notes/{id}/comments | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /oauth/token | v1 | v1 | excluded by choice: read-only tool | OAuth only | 0 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /oauth/token/ | v1 | v1 | excluded by choice: read-only tool | OAuth only | 0 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /organizationFields | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /organizationFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /organizationRelationships | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /organizations | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /organizations/{id}/followers | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /personFields | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /personFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /persons | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /persons/{id}/followers | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /persons/{id}/picture | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /phases | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /pipelines | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /productFields | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /productFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /products | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /products/{id}/duplicate | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /products/{id}/followers | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /products/{id}/images | v2 | v2 | excluded by choice: read-only tool | x-api-token | 20 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /products/{id}/variations | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /projectFields | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /projectFields/{field_code}/options | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /projects | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /projects/{id}/archive | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 3 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /roles | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /roles/{id}/assignments | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /roles/{id}/settings | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /stages | v2 | v2 | excluded by choice: read-only tool | x-api-token | 5 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /tasks | v2 | v1, v2 | excluded by choice: read-only tool | x-api-token | v1: 10 / v2: 5 | Both v1 and v2 publish this method+path. Tool uses v2 by choice. Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /users | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| POST | /webhooks | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /activityTypes/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /dealFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /deals/{id}/merge | v1 | v1 | excluded by choice: read-only tool | x-api-token | 40 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /files/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /filters/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /goals/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /legacyTeams/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /mailbox/mailThreads/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /notes/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /notes/{id}/comments/{commentId} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /organizationFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /organizationRelationships/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /organizations/{id}/merge | v1 | v1 | excluded by choice: read-only tool | x-api-token | 40 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /personFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /persons/{id}/merge | v1 | v1 | excluded by choice: read-only tool | x-api-token | 40 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /productFields/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /products/{id}/images | v2 | v2 | excluded by choice: read-only tool | x-api-token | 20 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /projects/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /projects/{id}/plan/activities/{activityId} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /projects/{id}/plan/tasks/{taskId} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /roles/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /roles/{id}/pipelines | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /tasks/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
| PUT | /users/{id} | v1 | v1 | excluded by choice: read-only tool | x-api-token | 10 | Write, edit, or state-changing path; excluded by read-only-by-choice policy. |
