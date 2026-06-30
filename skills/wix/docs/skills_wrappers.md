# Skills wrappers

This page explains how the current Wix skill wrapper is exposed for agent runtimes that support skills.

Most end users do not need this page first. It is here for the source install path and for builders maintaining the Wix wrapper.

## Core safeguards

- Skills are instructions; the CLI enforces safety.
- Keep the same safety loop:
  - dry-run -> review -> apply -> verify -> receipt
- Keep reads first.
- Keep to the implemented command surface while the official Wix coverage is accounted in docs/api_coverage.md.
- Stores Products V3 now ships the full current method set: reads/helpers, lifecycle writes, bulk writes, inventory-coupled writes, info-section helpers, category helpers, and variant filter helpers. Writes are reviewed-plan commands; destructive delete/remove helpers also require `--ack-irreversible`; the docs keep the Catalog V3-only boundary, read/write permission split, admin-read note for non-visible products, revision requirement, and no-full-variant-detail limit explicit; and the family remains live-unverified.
- Stores Inventory Items V3 is now the next bounded Stores slice in the shipped subset: `get`, `query`, and `search` are live reads/helpers; `create` and `update` are reviewed-plan writes; `delete` is an irreversible reviewed-plan write that also requires `--ack-irreversible`; the docs keep the Stores-app prerequisite, inventory read/write permission split, variant-location uniqueness rule, revision requirement, default-location inventory note, and search/query paging limits explicit; and the family remains live-unverified.
- Stores Locations V3 is now the next read-only Stores slice in the shipped subset: `get` and `query` are live reads/helpers; the docs keep the Stores-app prerequisite, inventory-only location scope, `INVENTORY` location-type rule, default-location note, and the separation from the broader Wix Locations create/update API explicit; and the family remains live-unverified.
- Catalog Versioning is now also shipped in the Stores subset: `get` is a live read/helper; the docs keep the V1-versus-V3 boundary, no-parameter contract, permanent-per-site note, and Stores-app prerequisite explicit; and the family remains live-unverified.
- Bookings Time Slots V2 is now the shipped availability slice for Bookings reads: `list-availability`, `get-availability`, `list-event`, `get-event`, `list-multi-service`, and `get-multi-service` are live reads/helpers; the docs keep the Wix Bookings app prerequisite, the `Read Bookings Calendar Availability` permission, the `SCOPE.DC-BOOKINGS.READ-CALENDAR` scope, the APP/MEMBER/VISITOR identity notes, the `get-event` Developer Preview note, and the live-unverified boundary explicit.
- Bookings Reader V2 is now the next bounded Bookings slice in the shipped subset: `query-extended-bookings` and `count-extended-bookings` are live reads/helpers; the docs keep the Wix Bookings app prerequisite, the three listed permissions, the no-get-by-id rule, the query limit and default sort, the `scheduleId` note for course bookings, the optional `withBookingAllowedActions` flag, the UTC date-filter rule, and the live-unverified boundary explicit.
- Bookings Services V2 is now the next Bookings slice in the shipped subset: reads/helpers inspect services, query supporting records, validate slugs, and list add-on groups; writes use reviewed plans; destructive or replace-style service operations also require `--ack-irreversible`; and service events stay callback-only.
- Bookings Resources V2 is now the next Bookings slice in the shipped subset: reads/helpers inspect non-staff resources; writes use reviewed plans; delete operations also require `--ack-irreversible`; update requires the current resource revision; Resource Types V2 stays separate; and staff resources stay outside this family because Wix manages them automatically.
- Bookings Resource Types V2 is now the next Bookings slice in the shipped subset: reads/helpers inspect resource classifications; writes use reviewed plans; delete also requires `--ack-irreversible` because Wix deletes connected resources; update requires the current resource type revision; and staff resource types stay outside this family because Wix manages them automatically.
- Bookings Staff Members is now the next Bookings slice in the shipped subset: reads/helpers inspect active and deleted staff; writes use reviewed plans; delete and trash-bin removal also require `--ack-irreversible`; update requires the current staff member revision; bulk tag update by IDs is capped at 100 staff members; and staff resource management stays inside this family because Wix manages staff resources automatically.
- Booking Policies is now the next Bookings slice in the shipped subset: reads/helpers inspect policies and calculate the strictest policy; writes use reviewed plans; delete and default-policy changes also require `--ack-irreversible`; update requires the current booking policy revision; and policy snapshots/service-plugin boundaries stay outside this family.
- Booking Policy Snapshots is now the next Bookings read slice in the shipped subset: `bookings-policy-snapshots list` retrieves saved policy snapshots by booking IDs; snapshots cannot be created through this API; and the Booking Policy Service Plugin stays outside the CLI as a Developer Preview service-plugin boundary.
- Bookings Attendance is now a shipped Bookings slice: reads/helpers inspect and count attendance, writes use reviewed plans, delete operations also require `--ack-irreversible`, and `count` is Developer Preview/member-auth-only.
- Bookings Waitlist is now the next Bookings slice in the shipped subset: `list` reads waitlisted entries, `register` creates a pending waitlist booking through reviewed plans, and `leave`/`book` are irreversible reviewed-plan writes because they cancel a pending booking or enroll a member. Wix marks all Waitlist methods Developer Preview, and writes require `--ack-event-session` because Wix limits Waitlist to `EVENT` sessions.
- Calendar Schedules V3 is now a shipped Calendar family: `get` and `query` read schedules, `create` and `update` use reviewed plans, and `cancel` is an irreversible reviewed-plan write. Bookings-visible schedules must use Wix Bookings app ID `13d21c63-b5ec-5912-8397-c3a5ddb27a97`, and schedule events stay callback-only.
- Calendar Skills / default business hours is a docs-only recipe, not a command family. Use the shipped `calendar-schedules-v3 query` and `calendar-events-v3 query|bulk-update|bulk-cancel|bulk-create` commands for that workflow; do not invent `calendar-skills`.
- Captcha is gated and non-callable in this REST CLI. Official Wix docs expose Developer Preview Authorize for Wix site or Blocks app backend code, but the Captcha introduction says Headless or REST API users cannot use the API. Do not invent `captcha authorize`.
- Bookings External Calendar V2 is now a shipped Bookings calendar family: provider, connection, calendar, and event commands are reads/helpers; credentials/OAuth connect and sync-config update use reviewed plans; credentials plans and receipts redact secret fields; and disconnect is an irreversible reviewed-plan write. Legacy Bookings Calendar V1 stays compatibility-only.
- Bookings Service Options and Variants is now a shipped Bookings services family: `get`, `get-by-service-id`, and `query` are reads/helpers; `create`, `update`, and `clone` use reviewed plans; and `delete` is an irreversible reviewed-plan write because it removes varied pricing from the service.
- Bookings course flow is accounted through existing explicit command families, not a separate course command: services expose course schedule/capacity, service options expose variants, Reader V2 queries existing course bookings, and Writer V2 creates course bookings with `booking.bookedEntity.schedule.scheduleId`. Time Slots V2 does not cover course availability, and Forms/checkout dependencies stay in their own coverage rows.
- Bookings Validation Service Plugin is accounted but not exposed as a CLI command: official Wix docs define provider-hosted Developer Preview callbacks under `{DEPLOYMENT-URI}`, so this tool records the boundary without adding a runnable command.
- Order Billing is now the full current official family in this tool: `get-order-refundability` and `calculate-refund` are live reads/helpers; `authorize-charge-with-saved-payment-method`, `capture-authorized-payments`, `void-authorized-payments`, `generate-receipts`, `redeem-gift-card`, and `refund-payments` are reviewed-plan writes; capture, void, redeem, and refund also require `--ack-irreversible`; and verification stays provider-response-first with refundability reread where the current read surface can prove it. Official docs say authorization needs a saved payment method, capture/void only work on authorized payments, capture is currently full-amount only, and `generate-receipts` plus `redeem-gift-card` are Developer Preview.
- Payments Cashier Transactions is now shipped as a read-only command: `payments transactions-list`. It lists transactions through the official query-parameter method, supports the documented pagination and filter flags, keeps the deprecated `currency` and `appId` filters honest, and leaves payment-provider/checkout plugin surfaces outside the CLI because they are callback or hosted flows.
- Use only explicit boundary commands from `docs/api_coverage.md` and `skills/wix/SKILL.md`.
- No free-form shell execution.
- Never include secrets in prompts or examples.

## Where the skill lives

- Source wrapper: `skills/wix/SKILL.md`.
- Public mirror wrapper: `SKILL.md`.
- Public install slug: `wix`.
- Users can copy or symlink the skill into their runtime skills folder.

## Wrapper command surface (declared boundary)

- Tool command: `wix-safe-agent-cli`
- Install slug in README: `wix`
- Local helper commands:
  - `onboarding`
  - `runs list`
  - `runs show`
- Auth and setup commands:
  - `auth check`
  - `auth token create`
  - `auth token request`
  - `auth token refresh`
  - `auth token inspect`
  - `auth token set`
  - `auth token status`
- Core family read families:
  - `contacts list|get|query`
  - `form-schemas list|get|query|count|get-deleted|list-deleted|query-deleted|count-deleted|list-providers-configs|get-summary|create|bulk-create|update|clone|bulk-clone|delete|bulk-delete|restore|remove-from-trash|bulk-remove-deleted-field`
  - `chat-settings get|query|create|update|delete`
  - `interactive-form-sessions create|create-streamed|send-message|send-message-streamed|generate-summary`
  - `intake-forms query|create-customer-submission-link|archive|unarchive|update-expiration-period|delete`
  - `intake-form-submissions query|search|count-by-intake-form-ids|list-data-by-contacts|cancel|extend|exempt|delete`
  - `community-groups list|get|get-by-slug|query|create|update|delete`
  - `community-group-rules list|create-or-replace`
  - `community-group-requests list|query|approve|reject`
  - `community-group-members list|list-memberships|query|query-memberships|add|remove`
  - `community-group-roles assign|unassign`
  - `community-join-requests list|query|approve|reject`
  - `community-membership-questions list|list-answers|create-or-replace`
  - `community-comments create|get|update|delete|moderate-draft-content|query|mark|unmark|hide|publish|count|list-by-resource|get-thread|bulk-publish|bulk-hide|bulk-delete|bulk-moderate-draft-content|bulk-move-by-filter`
  - `community-reports get|query|count-by-reason-types|create|update|upsert|delete|bulk-delete-by-filter`
  - `community-reviews get|query|count|create|update|delete|bulk-create|bulk-delete|remove-reply|set-reply|update-moderation-status|bulk-update-moderation-status`
  - `community-review-requests create|get|delete|query|count|bulk-cancel-by-filter`
  - `community-moderation-rules create|get|update|delete|query|check-content`
  - `inbox-conversations get|get-or-create`
  - `inbox-messages list|send`
  - `loyalty-program get|premium-features|update|activate|pause|enable-points-expiration|disable-points-expiration`
  - `loyalty-earning-rules list|get|create|update|delete|bulk-create|create-custom|delete-automation`
  - `loyalty-tiers list|get|create|update|delete|bulk-create|get-program|create-program-settings|get-program-settings|update-program-settings`
  - `loyalty-accounts list|get|query|search|count|get-program-totals|get-current-member-account|get-by-secondary-id|create|adjust-points|bulk-adjust-points|earn-points`
  - `loyalty-transactions get|query`
  - `loyalty-social-media list|create`
  - `loyalty-imports get|query|create-file-url|create|execute|get-error-file-download-url`
  - `loyalty-rewards list|get|query|create|bulk-create|update|delete`
  - `loyalty-checkout-discounts query|apply`
  - `loyalty-coupons get|query|get-current-member|redeem-current-member|redeem|delete`
  - `email-subscriptions query|upsert|bulk-upsert|generate-unsubscribe-link`
  - `members list|get|query|get-my|create|update|delete|delete-my|bulk-delete|approve|block|mute|unmute|disconnect|delete-addresses|delete-emails|delete-phones|bulk-approve|bulk-block|bulk-delete-by-filter|join-community|leave-community|update-member-slug|update-my-slug`
  - `activity-counters get|query|set`
  - `badges-v4 get|query|create|update|delete|move`
  - `badge-assignments query|create|delete|bulk-create|bulk-delete|bulk-update-tags|bulk-update-tags-by-filter`
  - `member-reports query|report|delete`
  - `members-followers follow|unfollow|list-followers|list-following|list-my-followers|list-my-following|query-connections|query-my-connections`
  - `user-members query`
  - `member-authentication send-set-password-email`
  - `member-abouts create|get|update|delete|query|get-my`
  - `member-privacy get-default|set-default|get-settings|set-settings`
  - `member-custom-fields create|update|delete|get|hide|list|update-order`
  - `member-custom-field-applications create|update|delete|get|list-applications|get-members|get-roles`
  - `member-custom-field-suggestions query|list`
  - `app-installations query|search`
  - `app-installation get-installed|is-permitted|install|install-from-share-url|uninstall|bulk-install|bulk-uninstall`
  - `app-instance get`
  - `bi-event send`
  - `embedded-scripts get`
  - `embedded-scripts embed`
  - `custom-embeds list|get|create|update|delete`
  - `benefit-items get|list|query|count|create|update|delete|bulk-create|bulk-delete|bulk-update|bulk-delete-by-filter`
  - `balances get|list|query|change|revert-change`
  - `bookings-time-slots-v2 list-availability|get-availability|list-event|get-event|list-multi-service|get-multi-service`
  - `bookings-reader-v2 query-extended-bookings|count-extended-bookings`
  - `bookings-services-v2 get|query|search|count|create|update|delete|bulk-create|bulk-update|bulk-update-by-filter|bulk-delete|bulk-delete-by-filter|query-policies|query-locations|query-categories|set-service-locations|enable-pricing-plans|disable-pricing-plans|set-custom-slug|validate-slug|clone|create-add-on-group|delete-add-on-group|list-add-on-groups-by-service-id|set-add-ons-for-group|update-add-on-group`
  - `bookings-resources-v2 get|query|search|count|create|update|delete|bulk-create|bulk-update|bulk-delete`
  - `bookings-resource-types-v2 get|query|count|create|update|delete`
  - `bookings-staff-members get|query|search|count|get-deleted|list-deleted|create|update|delete|assign-working-hours-schedule|bulk-update-tags|bulk-update-tags-by-filter|connect-to-user|disconnect-from-user|remove-from-trash`
  - `bookings-services-v2 get|query|search|count|create|update|delete|bulk-create|bulk-update|bulk-update-by-filter|bulk-delete|bulk-delete-by-filter|query-policies|query-locations|query-categories|set-service-locations|enable-pricing-plans|disable-pricing-plans|set-custom-slug|validate-slug|clone|create-add-on-group|delete-add-on-group|list-add-on-groups-by-service-id|set-add-ons-for-group|update-add-on-group`
  - `blog-posts-stats get|query|list|get-by-slug|get-metrics|get-total|query-count`
  - `blog-draft-posts get|query|list|get-deleted|list-deleted|create|update|delete|bulk-create|bulk-update|bulk-delete|publish|remove-from-trash-bin|restore-from-trash-bin`
  - `blog-categories get|query|list|get-by-slug|create|update|delete`
  - `blog-tags get|query|get-by-label|get-by-slug|create|delete`
  - `blog-likes create|get|delete|query|delete-by-fqdn-entity-id`
  - Forum is disabled/non-callable because Wix discontinued Forum on March 1, 2026.
  - `market-listing search`
  - `editor-deep-link create`
  - `site-plugins get-placement-status`
  - `app-permissions list`
  - `app-permissions create`
  - `app-permissions delete`
  - `contacts list|get|query|list-facets|query-facets|get-bulk-job|preview-merge|create|update|delete|merge|label|unlabel|bulk-delete|bulk-update|bulk-label-unlabel`
  - `form-schemas list|get|query|count|get-deleted|list-deleted|query-deleted|count-deleted|list-providers-configs|get-summary|create|bulk-create|update|clone|bulk-clone|delete|bulk-delete|restore|remove-from-trash|bulk-remove-deleted-field`
  - `chat-settings get|query|create|update|delete`
  - `interactive-form-sessions create|create-streamed|send-message|send-message-streamed|generate-summary`
  - `intake-forms query|create-customer-submission-link|archive|unarchive|update-expiration-period|delete`
  - `intake-form-submissions query|search|count-by-intake-form-ids|list-data-by-contacts|cancel|extend|exempt|delete`
  - `community-groups list|get|get-by-slug|query|create|update|delete`
  - `email-subscriptions query|upsert|bulk-upsert|generate-unsubscribe-link`
  - `contact-labels query`
  - `contact-labels list`
  - `contact-labels find-or-create`
  - `contact-labels get`
  - `contact-labels update`
  - `contact-labels delete`
  - `contact-extended-fields get`
  - `contact-extended-fields list`
  - `contact-extended-fields query`
  - `contact-extended-fields find-or-create`
  - `contact-extended-fields update`
  - `contact-extended-fields delete`
  - `contact-notes get`
  - `contact-notes query`
  - `contact-notes create`
  - `contact-notes update`
  - `contact-notes delete`
  - `contact-attachments get`
  - `contact-attachments list`
  - `contact-attachments generate-upload-url`
  - `contact-attachments delete`
  - `crm-tasks create|get|update|delete|query|count|move-after`
  - `crm-pipelines create|get|update|delete|query|bulk-update-tags|bulk-update-tags-by-filter`
  - `crm-cards create|get|update|delete|query|search|bulk-update-tags|bulk-update-tags-by-filter|move|search-by-stage`
  - `ai-site-chat-widget-settings get|set`
  - `ai-site-chat-widget-settings-v2 get|update`
  - `ai-site-chat-conversations get`
  - `ai-site-chat-messages list`
  - `ai-site-chat-messages bulk-create`
  - `ai-site-chat-messages bulk-get-by-inbox`
  - `ai-site-chat-messages media-upload-url`
  - `data-indexes list`
  - `data-indexes create`
  - `data-indexes drop`
  - `data-folders get|create|update|delete|create-collection-reference|get-collection-references|delete-collection-reference`
  - `data-extension-schemas list|create|update|delete-user-defined-fields`
  - `data-permissions get`
  - `data-permissions get-my`
  - `data-permissions update`
  - `data-permissions add-special`
  - `data-permissions update-special`
  - `data-permissions remove-special`
  - `data-sharing list-policies`
  - `data-sharing get-policy`
  - `data-sharing list-shared-collections`
  - `data-sharing create-policy`
  - `data-sharing update-policy`
  - `data-sharing delete-policy`
  - `data-sharing connect`
  - `data-sharing disconnect`
  - `contributors query`
  - `contributors remove`
  - `contributors change-role`
  - `contributors change-contributor-location`
  - `ai-credits get-balance`
  - `analytics-data get`
  - `analytics-sessions get-list-job-result`
  - `analytics-sessions list-async`
  - `analytics-sessions mark-recordings-deleted`
  - `analytics-sessions mark-session-recorded`
  - `analytics-semantic-models list|get|query`
  - `automation-storage-items create|get|query|bulk-update-tags|bulk-update-tags-by-filter|update-counter-by|update-value`
  - `automations-v2 create|get|update|delete|query|validate`
  - `async-jobs get|list-items`
  - `branches get-default|get|query`
  - `site-search search`
  - `accounts get`
  - `accounts list-child-accounts`
  - `domains check-availability`
  - `domains suggest`
  - `domain-dns get-zone`
  - `domain-dns preview-zone`
  - `domain-dns create-zone`
  - `domain-dns update-zone`
  - `domain-dns delete-zone`
  - `dns-propagation get`
  - `tags list|get|create|update|delete`
  - `locations list`
  - `locations query`
  - `locations get`
  - `locations create`
  - `locations update`
  - `locations archive`
  - `locations set-default`
  - `site-properties get`
  - `site-properties update-business-contact`
  - `site-properties update-business-profile`
  - `site-properties update-business-schedule`
  - `site-properties update-consent-policy`
  - `cookie-consent-policy get-cookie-banner-settings|update-cookie-banner-settings|get-cmp-config|update-cmp-config|create-consent-config|get-consent-config|update-consent-config|delete-consent-config|query-consent-configs|bulk-create-consent-configs|bulk-delete-consent-configs|bulk-update-consent-configs|bulk-update-consent-config-tags|bulk-update-consent-config-tags-by-filter|list-apps-and-storage`
  - `dashboard-favorite-list create|update|delete|add-favorite|delete-favorite|get`
  - `faq-category-v2 create|get|update|delete|query|list|update-extended-fields`
  - `faq-question-entry-v2 list|create|get|delete|update|query|bulk-delete|bulk-update|set-labels|update-extended-fields`
  - `functions-v1 create|get|update|delete|query|bulk-update-tags|bulk-update-tags-by-filter`
  - `function-types get|query`
  - `function-templates get|query`
  - `function-productions create|update|delete`
  - `builderless-productions create|get|update`
  - `function-methods create|delete|query`
  - `function-activations upsert|delete`
  - `function-spi-configurations create|get|update|delete|query|validate`
  - `billable-items create|get|update|delete|query|search|bulk-create|bulk-delete|bulk-update|bulk-update-tags|bulk-update-tags-by-filter`
  - `payment-links create|get|delete|query|search|activate|deactivate|initiate-payment|send|set-note|update-extended-fields|bulk-update-tags|bulk-update-tags-by-filter`
  - `payment-link-payments query|search|issue-receipt`
  - `receipts create|get|query|get-latest-number|regenerate-document|send-email|update-extended-fields`
  - `receipt-presets create|get|update|delete|list|get-default|set-default|update-extended-fields`
  - `receipts-settings get|update`
  - `payment-link-settings get|update`
  - `headless-oauth-apps create|get|update|query`
  - `headless-authentication login-v2|retrieve-tokens|register-v2|change-password|logout|sign-on`
  - `headless-recovery send-recovery-email`
  - `headless-redirects create-redirect-session`
  - `headless-sitemap list-pages`
  - `headless-verification verify-during-authentication`
  - `site-urls get-editor-urls`
  - `site-urls list-published-site-urls`
  - `connected-domains list`
  - `connected-domains get`
  - `connected-domains get-setup-info`
  - `connected-domains create`
  - `connected-domains delete`
  - `files list|get|batch-get|search|query|list-deleted|update|bulk-delete|bulk-restore|generate-upload-url|generate-resumable-upload-url|import|generate-download-url`
  - `media-folders list|get|search|query|list-deleted|create|update|bulk-delete|bulk-restore|generate-download-url`
  - `rich-content-ricos convert-from|convert-to|validate`
  - `pro-gallery list-galleries|get-gallery|create-gallery|update-gallery|delete-gallery|list-gallery-items|get-gallery-item|create-gallery-item|update-gallery-item|delete-gallery-item|bulk-delete-gallery-items`
  - `form-submissions get-submission|query-submissions-by-namespace|count-submissions|get-media-upload-url|create-submission|update-submission|delete-submission|confirm-submission|bulk-mark-submissions-as-seen`
  - `analytics-data get`
  - `analytics-sessions get-list-job-result|list-async|mark-recordings-deleted|mark-session-recorded`
  - `automation-storage-items create|get|query|bulk-update-tags|bulk-update-tags-by-filter|update-counter-by|update-value`
  - `automations-v2 create|get|update|delete|query|validate`
  - `notifications notify`
  - `sites query`
  - `sites count`
  - `site-folders query|get-folder-by-site`
- Grouped shorthand for docs/tests:
  - `locations list|query|get|create|update|archive|set-default`
  - `app-permissions list|create|delete`
  - `embedded-scripts get|embed`
  - `custom-embeds list|get|create|update|delete`
  - `secrets list|get-value|create|patch|delete`
  - `sender-emails list|get|create|delete|get-or-create|send-verification-code|verify`
  - `sender-details list|get|create|update|delete|get-default|mark-default`
  - `sending-domains get|query|authenticate`
  - `marketing-consent get|query|get-by-identifier|create|update|delete|upsert|bulk-upsert|remove`
  - `referral-program get|get-premium-features|get-ai-social-media-posts-suggestions|activate|pause|generate-ai-social-media-posts-suggestions|update`
  - `referral-rewards get|query`
  - `referring-customers get|query|get-by-referral-code|generate-for-contact|delete`
  - `referred-friends get|query|get-by-contact-id|create|update|delete`
  - `referral-tracker get|query|get-statistics`
  - `email-campaigns list|get|get-audience|list-statistics|list-recipients|pause-scheduling|reschedule|send-test|publish|reuse|delete|identify-sender-address`
  - `donation-campaigns get|get-metrics|query|create|update|bulk-create|bulk-update|bulk-update-tags|bulk-update-tags-by-filter`
  - `benefit-items get|list|query|count|create|update|delete|bulk-create|bulk-delete|bulk-update|bulk-delete-by-filter`
  - `balances get|list|query|change|revert-change`
  - `pricing-plans get|query|search|count|create|update|delete|bulk-update`
  - `orders search|get|create|update|cancel|bulk-update`
  - `bookings-time-slots-v2 list-availability|get-availability|list-event|get-event|list-multi-service|get-multi-service`
  - `bookings-reader-v2 query-extended-bookings|count-extended-bookings`
  - `bookings-policies get|query|count|strictest|create|update|delete|set-default`
  - `bookings-policy-snapshots list`
  - `bookings-attendance get|query|count|set|bulk-set|delete|bulk-delete`
  - `bookings-waitlist list|register|leave|book`
  - `calendar-schedules-v3 get|query|create|update|cancel`
  - `calendar-schedule-time-frames-v3 get|list`
  - `calendar-events-v3 create|get|update|query|list|bulk-create|bulk-update|bulk-cancel|cancel|list-by-contact|list-by-member|restore-defaults|split-recurring`
  - `calendar-event-views-v3 get`
  - `calendar-participations-v3 create|get|update|delete|query`
  - `bookings-external-calendars-v2 list-providers|connect-by-credentials|connect-by-oauth|list-connections|get-connection|update-sync-config|list-calendars|list-events|disconnect`
  - `bookings-service-options-v1 get|get-by-service-id|query|create|update|delete|clone`
  - `bookings-resources-v2 get|query|search|count|create|update|delete|bulk-create|bulk-update|bulk-delete`
  - `bookings-resource-types-v2 get|query|count|create|update|delete`
  - `bookings-staff-members get|query|search|count|get-deleted|list-deleted|create|update|delete|assign-working-hours-schedule|bulk-update-tags|bulk-update-tags-by-filter|connect-to-user|disconnect-from-user|remove-from-trash`
  - `stores-products-v3 get|get-by-slug|get-all-products-category|query|search|count|create|update|delete|bulk-create|bulk-delete|bulk-update|create-with-inventory|update-with-inventory|bulk-create-with-inventory|bulk-update-with-inventory|bulk-add-info-sections|bulk-add-info-sections-by-filter|bulk-add-to-categories-by-filter|bulk-adjust-variants-by-filter|bulk-delete-by-filter|bulk-remove-info-sections|bulk-remove-info-sections-by-filter|bulk-remove-from-categories-by-filter|bulk-update-variants-by-filter|bulk-update-by-filter`
  - `read-only-variants-v3 query|search`
  - `brands-v3 get|query|create|update|delete|bulk-create|bulk-delete|bulk-update|get-or-create|bulk-get-or-create`
  - `ribbons-v3 get|query|create|update|delete|bulk-create|bulk-delete|bulk-update|get-or-create|bulk-get-or-create`
  - `stores-info-sections-v3 get|query|create|update|delete|bulk-create|bulk-delete|bulk-update|get-or-create|bulk-get-or-create`
  - `customizations-v3 get|query|create|update|delete|bulk-create|bulk-update|add-choices|bulk-add-choices|remove-choices|set-choices`
  - `categories get|get-by-slug|query|search|count|list-trees|get-arranged-items|list-categories-for-item|list-categories-for-items|list-items-in-category|create|update|delete|bulk-update|update-visibility|bulk-show|bulk-add-items-to-category|bulk-add-item-to-categories|bulk-remove-items-from-category|bulk-remove-item-from-categories|move|set-arranged-items`
  - `stores-inventory-items-v3 get|query|search|create|update|delete`
  - `stores-locations-v3 get|query`
  - `catalog-versioning get`
  - `order-billing get-order-refundability|calculate-refund|authorize-charge-with-saved-payment-method|capture-authorized-payments|void-authorized-payments|generate-receipts|redeem-gift-card|refund-payments`
  - `coupons get|query|create|update|delete|bulk-create|bulk-delete`
  - `gift-cards create|get|query|search|count|disable|send-email`
  - `campaign-validation validate-link|validate-html-links`
  - `events-settings get|update`
  - `portfolio-settings get|update`
  - `portfolio-collections create|get|update|delete|query|list`
  - `portfolio-projects create|get|update|delete|query|list|bulk-update`
  - `portfolio-project-items create|get|update|delete|list|bulk-create|bulk-update|bulk-delete|duplicate`
  - `suppliers-hub-products get|query|search|query-categories|create|update|delete|bulk-create|bulk-update|bulk-delete|bulk-add-to-store|bulk-update-tags|bulk-update-tags-by-filter`
  - `suppliers-hub-suppliers get|query|create|update|delete|bulk-create|bulk-update|bulk-delete|bulk-update-tags|bulk-update-tags-by-filter`
  - `suppliers-hub-marketplace-provider-submissions submit-generated-mockups`
  - `events-v3 create|get|update|delete|query|bulk-cancel-by-filter|bulk-delete-by-filter|cancel|clone|count-by-status|get-by-slug|list-by-category|publish-draft`
  - `events-ticket-definitions-v3 create|get|update|delete|query|bulk-delete-by-filter|change-currency|count|reorder`
  - `events-categories create|bulk-create|update|delete|query|assign-events|unassign-events|bulk-assign-events|bulk-unassign-events|get|reorder-events`
  - `events-schedule-items get|query|add|create-bookmark|delete-bookmark|delete|discard-draft|list-bookmarks|list|publish-draft|reschedule-draft|update`
  - `events-policies-v2 create|get|update|delete|query|reorder`
  - `events-staff-members create|get|update|delete|query`
  - `events-guests query`
  - `events-rsvps-v2 create|get|update|delete|query|search|bulk-update|bulk-delete-by-filter|check-in|cancel-check-in|count|list-summary`
  - `events-ticket-reservations create|get|delete|bulk-update-tags|bulk-update-tags-by-filter|cancel`
  - `events-tickets get|list|update|bulk-update|check-in|delete-check-in`
  - `events-orders list|get|update|bulk-update|confirm|get-summary|get-checkout-options|list-available-tickets|query-available-tickets|create-reservation|cancel-reservation|checkout|update-checkout|get-invoice`
  - `events-forms get-form|discard-draft|add-control|update-control|delete-control|update-messages|publish-draft`
  - `site-plugins get-placement-status`
  - `market-listing search`
  - `editor-deep-link create`
  - `contact-labels query|list|find-or-create|get|update|delete`
  - `data-indexes list|create|drop`
  - `data-folders get|create|update|delete|create-collection-reference|get-collection-references|delete-collection-reference`
  - `data-extension-schemas list|create|update|delete-user-defined-fields`
  - `data-permissions get|get-my|update|add-special|update-special|remove-special`
  - `data-sharing list-policies|get-policy|list-shared-collections|create-policy|update-policy|delete-policy|connect|disconnect`
  - `notifications notify`
  - `site-properties get|update-business-contact|update-business-profile|update-business-schedule|update-consent-policy`
  - `cookie-consent-policy get-cookie-banner-settings|update-cookie-banner-settings|get-cmp-config|update-cmp-config|create-consent-config|get-consent-config|update-consent-config|delete-consent-config|query-consent-configs|bulk-create-consent-configs|bulk-delete-consent-configs|bulk-update-consent-configs|bulk-update-consent-config-tags|bulk-update-consent-config-tags-by-filter|list-apps-and-storage`
  - `dashboard-favorite-list create|update|delete|add-favorite|delete-favorite|get`
  - `faq-category-v2 create|get|update|delete|query|list|update-extended-fields`
  - `faq-question-entry-v2 list|create|get|delete|update|query|bulk-delete|bulk-update|set-labels|update-extended-fields`
  - `functions-v1 create|get|update|delete|query|bulk-update-tags|bulk-update-tags-by-filter`
  - `function-types get|query`
  - `function-templates get|query`
  - `function-productions create|update|delete`
  - `builderless-productions create|get|update`
  - `function-methods create|delete|query`
  - `function-activations upsert|delete`
  - `function-spi-configurations create|get|update|delete|query|validate`
  - `billable-items create|get|update|delete|query|search|bulk-create|bulk-delete|bulk-update|bulk-update-tags|bulk-update-tags-by-filter`
  - `payment-links create|get|delete|query|search|activate|deactivate|initiate-payment|send|set-note|update-extended-fields|bulk-update-tags|bulk-update-tags-by-filter`
  - `payment-link-payments query|search|issue-receipt`
  - `receipts create|get|query|get-latest-number|regenerate-document|send-email|update-extended-fields`
  - `receipt-presets create|get|update|delete|list|get-default|set-default|update-extended-fields`
  - `receipts-settings get|update`
  - `payment-link-settings get|update`
  - `headless-oauth-apps create|get|update|query`
  - `headless-authentication login-v2|retrieve-tokens|register-v2|change-password|logout|sign-on`
  - `headless-recovery send-recovery-email`
  - `headless-redirects create-redirect-session`
  - `headless-sitemap list-pages`
  - `headless-verification verify-during-authentication`
  - `site-urls get-editor-urls|list-published-site-urls`
  - `analytics-sessions get-list-job-result|list-async|mark-recordings-deleted|mark-session-recorded`
  - `analytics-semantic-models list|get|query`
  - `automation-storage-items create|get|query|bulk-update-tags|bulk-update-tags-by-filter|update-counter-by|update-value`
  - `automations-v2 create|get|update|delete|query|validate`
  - `async-jobs get|list-items`
  - `branches get-default|get|query`
  - `site-search search`
  - `form-submissions get-submission|query-submissions-by-namespace|count-submissions|get-media-upload-url|create-submission|update-submission|delete-submission|confirm-submission|bulk-mark-submissions-as-seen`
  - `interactive-form-sessions create|create-streamed|send-message|send-message-streamed|generate-summary`
  - `intake-forms query|create-customer-submission-link|archive|unarchive|update-expiration-period|delete`
  - `intake-form-submissions query|search|count-by-intake-form-ids|list-data-by-contacts|cancel|extend|exempt|delete`
  - `data-collections list|get|create|update|patch|delete|create-field|update-field|patch-field|delete-field|add-plugin|delete-plugin`
- Account-level write families (`implemented`):
  - `projects create-project`
  - `site-actions bulk-delete`
  - `site-actions duplicate`
  - `site-actions publish`
  - `site-folders create`
  - `site-folders update`
  - `site-folders delete`
  - `site-folders move-folders`
  - `site-folders move-sites`
- CMS families (`implemented`):
  - `data-items get|query|count|aggregate|aggregate-pipeline|distinct|search|query-referenced|is-referenced`
  - `data-items insert-reference|remove-reference|replace-references`
  - `data-items insert|save|truncate|bulk-insert|bulk-patch|bulk-remove|bulk-save|bulk-update|bulk-insert-references|bulk-remove-references|update|patch|remove`
  - `data-collections list|get`
  - `data-collections create|update|patch|delete`
  - `data-collections create-field`
  - `data-collections update-field`
  - `data-collections patch-field`
  - `data-collections delete-field`
  - `data-collections add-plugin`
  - `data-collections delete-plugin`
- The shipped wrapper only covers the explicit real command families listed here. It does not expose a generic demo command or a generic batch-runner command.

## What the skill must include

- Reads run live with `--output json`.
- Prefer `--output json` for predictable agent-readable output.
- Writes stay plan-first:
  - `--plan-out` to create a reviewed draft plan
  - `--plan-in` to apply a prepared plan
  - `--apply --yes` to execute after explicit approval
  - `--receipt-out` to capture write proof
- Include `--ack-irreversible` when the selected write command requires it.
- For the risky Wix write families in this tool, do not skip straight to `--apply --yes`; use a reviewed saved plan first.
- Bookings Validation Service Plugin is accounted as a callback-only Developer Preview boundary, not a CLI command.
- `locations` writes (`create`, `update`, `set-default`) are plan-first and `locations archive` also needs `--ack-irreversible`.
- `locations update` is full-object replacement and uses reread verification.
- `tags` writes (`create`, `update`, `delete`) are plan-first. `tags delete` also needs `--ack-irreversible`, and receipts keep manual-only recovery explicit.
- `files` reads are live reads. `files update`, `bulk-delete`, `bulk-restore`, and `import` are reviewed-plan writes. `files bulk-delete` also needs `--ack-irreversible`. `generate-upload-url`, `generate-resumable-upload-url`, and `generate-download-url` are non-mutating helper calls that return official Wix helper URLs.
- `media-folders` reads are live reads. `media-folders create`, `update`, `bulk-delete`, and `bulk-restore` are reviewed-plan writes. `media-folders bulk-delete` also needs `--ack-irreversible`, and `bulk-restore` keeps no-snapshot recovery limits explicit.
- Wix Skills / Media skills is docs-only, not a CLI command family. Official Wix Skills docs describe installable `SKILL.md` instructions for AI tools; the callable Media Manager API remains `files` and `media-folders`.
- Account Level Sites Skills is docs-only, not a CLI command family. Official Wix docs describe recipes that use existing APIs; use `sites query`, `projects create-project`, `site-actions publish`, and `headless-oauth-apps create` for the shipped explicit pieces.
- `resellers` covers the official Account Level Resellers package and product-instance API. Reads use account-level API-key auth. Writes are reviewed-plan commands, and `cancel-package` plus `cancel-product-instance` also require `--ack-irreversible` because they remove customer access.
- Resellers commands are `resellers get`, `resellers query`, `resellers create-package`, `resellers adjust-product-instance`, `resellers assign-product-instance`, `resellers unassign-product-instance`, `resellers update-package-external-id`, `resellers cancel-package`, and `resellers cancel-product-instance`.
- HTTP Functions is site-defined and non-callable in this generic safe CLI. Official docs expose a custom Velo function invoker by `functionName`; do not add a generic `http-functions call` command because that would be a call-anything bridge.
- `rich-content-ricos convert-from`, `convert-to`, and `validate` are non-mutating POST helpers for official Ricos Documents conversion and validation. They require `Manage Ricos Document` and remain live-unverified.
- `pro-gallery` reads inspect galleries and gallery items. `create-gallery`, `update-gallery`, `create-gallery-item`, and `update-gallery-item` are reviewed-plan writes. `delete-gallery`, `delete-gallery-item`, and `bulk-delete-gallery-items` also need `--ack-irreversible`. Official docs say API-created galleries are backend-only until connected manually in the Wix Editor, media items must already exist in Media Manager, and the deprecated Delete Gallery Items method should be replaced by Bulk Delete Gallery Items.
- `site-properties` writes are plan-first, `update-business-schedule` is overwrite-style, and all writes are read-after-write verified.
- `notifications notify` is plan-first. `--notification-template-id` is required, `--dynamic-values-json` must map placeholders to `text` only, and this boundary uses Wix app or Wix user identity auth for the site context.
- `notifications notify` needs `Manage Notifications` (`SCOPE.DC-NOTIFICATIONS.MANAGE-NOTIFICATIONS`) and provider usage is up to 100,000 calls per month per site.
- `notifications notify` is implemented but live-unverified: success currently depends only on `notificationBatchId` in the provider response, not proof of delivery.
- `multilingual-locale-settings` covers the official Wix Multilingual Locale Settings API. Commands are `multilingual-locale-settings get`, `multilingual-locale-settings set-mode`, and `multilingual-locale-settings update`. Writes are reviewed-plan commands; applying `set-mode --enabled false` also requires `--ack-irreversible` because Wix says disabling multilingual mode removes translated content and resets locale settings.
- `multilingual-locales` covers the official Wix Multilingual Locales API. Commands are `multilingual-locales create`, `multilingual-locales get`, `multilingual-locales update`, `multilingual-locales delete`, `multilingual-locales query`, `multilingual-locales bulk-create`, `multilingual-locales bulk-delete`, `multilingual-locales bulk-update`, `multilingual-locales create-new-primary`, `multilingual-locales get-new-primary-status`, `multilingual-locales list-supported`, and `multilingual-locales set-visitor-primary`. Locale deletes and primary-locale changes require `--ack-irreversible`.
- `multilingual-translation-schemas` covers the official Wix Multilingual Translation Schema API. Commands are `multilingual-translation-schemas create`, `multilingual-translation-schemas get`, `multilingual-translation-schemas update`, `multilingual-translation-schemas delete`, `multilingual-translation-schemas query`, `multilingual-translation-schemas list-site`, and `multilingual-translation-schemas get-by-key`. Writes are reviewed-plan commands; schema deletes and updates that remove fields require `--ack-irreversible`.
- `multilingual-translation-contents` covers the official Wix Multilingual Translation Content API. Commands are `multilingual-translation-contents create`, `multilingual-translation-contents get`, `multilingual-translation-contents update`, `multilingual-translation-contents delete`, `multilingual-translation-contents query`, `multilingual-translation-contents search`, `multilingual-translation-contents bulk-create`, `multilingual-translation-contents bulk-delete`, `multilingual-translation-contents bulk-update`, `multilingual-translation-contents bulk-update-by-key`, and `multilingual-translation-contents update-by-key`. Writes are reviewed-plan commands; deletes, bulk deletes, and updates that remove fields require `--ack-irreversible`. Content events are callback-only.
- `multilingual-translation-published-contents` covers the official Wix Multilingual Translation Published Content API. The callable command is `multilingual-translation-published-contents query`; it is read-only and requires the official `schemaKey.appId`, `schemaKey.entityType`, and `schemaKey.scope` filters. Published content events are callback-only.
- `multilingual-machine-translation` covers the official Wix Multilingual Machine Translation API. Commands are `multilingual-machine-translation translate` and `multilingual-machine-translation bulk-translate`. Both are reviewed-plan commands; successful translation consumes word credits, so live apply requires `--ack-irreversible`.
- `multilingual-machine-translation-credit-data` covers the official Wix Multilingual Machine Translation Credit Data API. Commands are `multilingual-machine-translation-credit-data get` and `multilingual-machine-translation-credit-data check-sufficient`. These are read/helper commands; `check-sufficient` uses the official `wordCount` body and does not spend credits.
- `online-programs-programs` covers the official Wix Online Programs Programs API. Commands are `online-programs-programs create`, `get`, `update`, `delete`, `query`, `search`, `count`, `bulk-update`, `archive`, `duplicate`, `end`, `list-samples`, and `publish`. Writes are reviewed-plan commands; `delete`, `archive`, and `end` require `--ack-irreversible`.
- Full Online Programs command names are `online-programs-programs create`, `online-programs-programs get`, `online-programs-programs update`, `online-programs-programs delete`, `online-programs-programs query`, `online-programs-programs search`, `online-programs-programs count`, `online-programs-programs bulk-update`, `online-programs-programs archive`, `online-programs-programs duplicate`, `online-programs-programs end`, `online-programs-programs list-samples`, and `online-programs-programs publish`.
- `online-programs-instructor-v2` covers the official Wix Online Programs Instructor V2 API. Commands are `online-programs-instructor-v2 create`, `online-programs-instructor-v2 update`, `online-programs-instructor-v2 query`, `online-programs-instructor-v2 assign`, `online-programs-instructor-v2 change-program-instructors`, `online-programs-instructor-v2 invite`, `online-programs-instructor-v2 list`, and `online-programs-instructor-v2 unassign`. Writes are reviewed-plan commands; `invite`, `change-program-instructors`, and `unassign` require `--ack-irreversible`.
- `b2b-site-transfer` covers the official Wix B2B Site Management Business Site Transfer V1 method. Command is `b2b-site-transfer transfer`. It uses account-level API-key auth with `wix-account-id` as the target account header, requires `siteTransfer.siteId` and `siteTransfer.sourceAccountId`, and live apply requires `--ack-irreversible`.
- `partner-profiles` covers the official Developer Preview Wix Partner Profile V1 API. Commands are `partner-profiles create`, `partner-profiles update`, `partner-profiles delete`, `partner-profiles get-current`, `partner-profiles get-public`, and `partner-profiles find-public-by-slug`. Owner-facing commands use account-level API-key auth; public reads use no auth; `partner-profiles delete` requires `--ack-irreversible`; and the official `contact-partner` method is first-party-only and not exposed.
- `viewer-cache` and `viewer-seo-tags` cover the official Wix Viewer Cache and SEO Tags APIs. Commands are `viewer-cache invalidate`, `viewer-seo-tags resolve-item`, and `viewer-seo-tags resolve-static`. Cache invalidation is reviewed-plan and limited by Wix to developing sites using Web Methods or Router APIs; SEO tag resolution commands are read-only.
- GraphQL is docs-only/non-callable in this safe CLI. Official Wix GraphQL docs describe arbitrary queries and mutations against a unified schema, so no generic `graphql` bridge command is exposed.
- Generic async job runner is docs-only/non-callable. Official Async Job read methods are already shipped as `async-jobs get` and `async-jobs list-items`; no generic job runner command is exposed.
- `site-urls` methods are read-only.
- `app-instance get` is read-only, app-token based, and uses the app installation context of this tool.
- `bi-event send` is a reviewed-plan write that uses `--plan-out` then `--plan-in --apply --yes`. It sends one named Wix BI event and keeps the no-rollback limit explicit.
- `embedded-scripts get` is read-only, uses this CLI's existing token-based app path, and keeps the current Wix docs auth mismatch explicit: the family intro says Wix App while the method page says Wix app or Wix user identity.
- `embedded-scripts embed` is the reviewed-plan write for the same family. It uses `--plan-out` then `--plan-in --apply --yes`, captures a before-state snapshot from the get method, and verifies apply with a read-after-write check.
- `custom-embeds list` and `custom-embeds get` are read-only methods for site custom embed state.
- `custom-embeds create`, `custom-embeds update`, and `custom-embeds delete` are reviewed-plan writes. `delete` also needs `--ack-irreversible`, and `update` requires the current revision number.
- The Custom Embeds family intro and write pages say Wix app or Wix user identity auth, while the get/list pages prominently show permission and endpoint details but may omit the auth paragraph. This boundary keeps that docs inconsistency explicit and stays live-unverified.
- Custom embed HTML/JS is live site code, so verification is reread-based and recovery is manual only.
- `secrets list` is a read-only metadata command and never returns secret values.
- `secrets get-value` is a read command that returns the real secret value, so keep it in backend-safe workflows only.
- `secrets create`, `secrets patch`, and `secrets delete` are reviewed-plan writes.
- `secrets delete` also requires `--ack-irreversible`.
- Plans and receipts never store secret values. They keep metadata only.
- Wix docs say the Members Area app must be installed before a site can create or manage secrets, but it is not required for `secrets get-value`.
- Wix docs also say deleting a secret, or changing its name or value, breaks code using that secret.
- `sender-emails list` and `sender-emails get` are live reads.
- `sender-emails create`, `sender-emails delete`, `sender-emails get-or-create`, `sender-emails send-verification-code`, and `sender-emails verify` are reviewed-plan writes.
- `sender-emails delete` requires `--ack-irreversible`.
- `sender-emails send-verification-code` only proves provider acceptance here; inbox delivery is outside this CLI.
- `sender-emails verify` rereads the sender email and expects `verified: true`.
- `sender-details list`, `sender-details get`, and `sender-details get-default` are live reads.
- `sender-details create`, `sender-details update`, `sender-details delete`, and `sender-details mark-default` are reviewed-plan writes.
- `sender-details delete` requires `--ack-irreversible`.
- Wix docs say sender details can only use verified sender email addresses.
- `sending-domains get` and `sending-domains query` are live reads.
- `sending-domains authenticate` is a reviewed-plan write and this wrapper refuses it unless the current status is `NOT_AUTHENTICATED`.
- Official sending-domain docs require query filtering by `domain` or `id` and note that DNS propagation can take up to 48 hours.
- `marketing-consent get`, `query`, and `get-by-identifier` are live reads.
- `marketing-consent create`, `update`, `upsert`, `bulk-upsert`, and `remove` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `marketing-consent delete` is an irreversible reviewed-plan delete that also requires `--ack-irreversible`.
- `marketing-consent query` returns up to 100 items per request and defaults to sort `id ASC`.
- `marketing-consent create` is limited here to confirmed single-confirmation consent and refuses existing identifiers so the caller must switch to `upsert`.
- `marketing-consent update` requires `--mask-json` plus a payload `id`, and existing email consent state stays at the provider’s current value if the caller tries to patch it to `UNKNOWN_STATE`.
- `marketing-consent upsert` is the path for double-confirmation or other state changes.
- `marketing-consent bulk-upsert` accepts a raw array or an `info` object and enforces the official `500`-item limit before send.
- `marketing-consent remove` changes the state to `REVOKED` but does not delete the entity.
- The official `get-by-identifier` page currently renders the query parameters badly, and the official `remove` page says `lastRevokeActivity` is required even though the curl example omits it. This wrapper keeps both docs quirks explicit and stays strict on revoke input.
- `referral-program get`, `get-premium-features`, and `get-ai-social-media-posts-suggestions` are live reads.
- `referral-program activate`, `pause`, `generate-ai-social-media-posts-suggestions`, and `update` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- Official Referral Program docs require a qualifying Wix site plan, at least one supported Wix business app, and only one referral program per site.
- `referral-program update` requires the current program revision, and Program Updated stays callback-only.
- `referral-rewards get` and `query` are live read/helper commands for referral reward records. Official docs require a qualifying Wix site plan, at least one supported Wix business app, Wix app or Wix user identity auth, and `Manage Referrals`.
- `referring-customers get`, `query`, and `get-by-referral-code` are live read/helper commands for referring customer records. `generate-for-contact` is a reviewed-plan write using a `contactId` body, and `delete` is an irreversible reviewed-plan delete that sends the current `revision` as a REST query parameter. Official docs require a qualifying Wix site plan, at least one supported Wix business app, Wix app or Wix user identity auth, and `Manage Referrals`.
- `referred-friends get`, `query`, and `get-by-contact-id` are live read/helper commands for referred friend records. `create` is a reviewed-plan write using a 12-character `referralCode`, `update` is a reviewed-plan write using the official `referredFriend` object and current `revision`, and `delete` is an irreversible reviewed-plan delete that sends the current `revision` as a REST query parameter. Official docs require a qualifying Wix site plan, at least one supported Wix business app, `Manage Referrals`, and member identity for create.
- `referral-tracker get`, `query`, and `get-statistics` are live read/helper commands for referral events and referral statistics. Official docs require the Wix Loyalty Program app, a qualifying Wix site plan, at least one supported Wix business app, Wix app or Wix user identity auth, and `Manage Referrals`.
- `email-campaigns list`, `get`, `get-audience`, `list-statistics`, `list-recipients`, and `identify-sender-address` are live read/helper calls in this campaign slice. `publish`, `reuse`, `pause-scheduling`, `reschedule`, `send-test`, and `delete` are reviewed-plan writes. `pause-scheduling` rereads the campaign and expects `distributionStatus=PAUSED`. `reschedule` is provider-response-only because the current read surface does not prove the scheduled time directly. `send-test` is rate-limited in the official docs and is provider-response-only here because inbox delivery happens outside this CLI. `publish` may be landing-page-only when no email distribution options are supplied, `reuse` creates a new campaign copy, and `delete` is permanent and requires `--ack-irreversible`.
- `donation-campaigns get`, `get-metrics`, and `query` are live reads.
- `donation-campaigns create`, `update`, `bulk-create`, `bulk-update`, `bulk-update-tags`, and `bulk-update-tags-by-filter` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- Official Wix docs say Wix Donations must be installed, the current command set uses `Manage Donation Campaigns`, `query` defaults to `createdDate ASC` with `cursorPaging.limit 100`, `create` and `bulk-create` require `customAmountEnabled`, `predefinedDonationAmounts`, or both, campaign status is automatic, and `update` / `bulk-update` require the current `revision`.
- `donation-campaigns get-metrics` returns aggregated totals only, needs a configured `campaignGoal`, and stays in the site's default currency. `bulk-update-tags-by-filter` is async and this wrapper verifies returned `jobId` only. Although official docs allow an empty filter, this boundary refuses empty-filter all-campaign retagging.
- `benefit-items get`, `list`, `query`, and `count` are live reads.
- `benefit-items create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `benefit-items delete`, `bulk-delete`, and `bulk-delete-by-filter` are destructive reviewed-plan writes and also require `--ack-irreversible`.
- Official Wix docs say sites using this API must install the Pricing Plans app. Reads use `SCOPE.BENEFIT_PROGRAMS.READ (PII)`, writes use `Manage benefit programs` / `SCOPE.BENEFIT_PROGRAMS.MANAGE`, `query` defaults to paging limit `50`, `list` returns up to `1000` items, `update` and `bulk-update` require the current `revision`, and this boundary refuses empty-filter bulk delete.
- `balances get`, `list`, and `query` are live reads.
- `balances change` and `balances revert-change` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- Official Wix docs say sites using this API must install the Pricing Plans app. Reads use `SCOPE.BENEFIT_PROGRAMS.READ (PII)`, writes use `Manage benefit programs`, `query` defaults to paging limit `50`, supported filters include `id`, `createdDate`, `beneficiary.memberId`, and `beneficiary.wixUserId`, and `revert-change` is a specific transaction undo path rather than a blanket rollback promise.
- `pricing-plans get`, `query`, `search`, and `count` are live reads.
- `pricing-plans create` and `update` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `pricing-plans delete` is an irreversible reviewed-plan delete that also requires `--ack-irreversible`.
- `pricing-plans bulk-update` is a reviewed-plan bulk write with `--plan-out` then `--plan-in --apply --yes`. This tool rejects duplicate target plan IDs, rejects plan-name changes in bulk update, normalizes either a raw plans array or a full body object into the official request body, and defaults `returnEntity` to `true` when omitted so verification has fuller provider context.
- Official Wix docs say reads use `Read Orders` and `Read Pricing Plans`, while writes use `Manage Pricing Plans`.
- `pricing-plans query` defaults to `createdDate ASC` with `cursorPaging.limit 100`, `search` can include aggregations, the update page currently renders the path placeholder as `{plan.id}`, and official bulk-update docs say one request can include up to `100` plans and can't change plan names.
- `gift-cards get`, `query`, `search`, and `count` are live reads.
- `gift-cards create`, `disable`, and `send-email` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `gift-cards disable` is an irreversible reviewed-plan write and also requires `--ack-irreversible`.
- Official Wix docs say the Wix Gift Card app must be installed, all shipped methods use `Manage eCommerce - all permissions`, `send-email` also needs a premium site plan, gift card codes are obfuscated outside the create response, `count` is currently Developer Preview, and the deprecated list-by-email method stays out of this shipped subset.
- `orders search` and `get` are live reads, while `orders create`, `update`, and `bulk-update` are reviewed-plan writes and `orders cancel` is an irreversible reviewed-plan write requiring `--ack-irreversible`. Official Wix docs say Orders uses Wix app or Wix user identity auth with `Manage Orders`, `create` is for manual or external-system orders, `update` only covers the documented subset of order fields, `bulk-update` supports up to `100` orders, and `cancel` changes status to `CANCELED` with no automatic rollback and possible buyer-email or restock side effects.
- `campaign-validation validate-link` and `validate-html-links` are live read/helper validation calls.
- Official Wix docs say campaigns must already exist in Wix before API access, the site email-marketing account must be `ACTIVE` with quota available, `list-statistics` supports up to 100 campaign IDs, and `list-recipients` requires an `activity` filter.
- Campaign lifecycle writes are now shipped in the current subset: `pause-scheduling`, `reschedule`, `send-test`, `publish`, `reuse`, and `delete`.
- `market-listing search` is read-only, uses this CLI's existing token-based app path, is marked Developer Preview in the official docs, and returns published app listings only.
- `editor-deep-link create` is a helper POST that returns a URL. It keeps the legacy-custom-element-only note explicit and does not claim that the site has already changed.
- `form-submissions` methods are mixed: read/helper + reviewed-plan writes. All commands require the `wix_forms` app check through internal app-instance validation.
- `app-permissions list` follows the shipped app/user-token command path in this tool and is read-only.
- `app-permissions create` and `app-permissions delete` are reviewed-plan writes and use account API-key auth (`Authorization` + `wix-account-id`).
- This family is implemented but live-unverified because all three official method pages currently render `/apps/v1/app-permissions/v1/app-permissions` with mixed auth text.
- `contacts list`, `contacts get`, `contacts query`, `contacts list-facets`, `contacts query-facets`, `contacts get-bulk-job`, and `contacts preview-merge` are live reads in this boundary.
- `contacts create`, `contacts update`, `contacts label`, and `contacts unlabel` are reviewed-plan writes.
- `contacts delete`, `contacts merge`, `contacts bulk-delete`, `contacts bulk-update`, and `contacts bulk-label-unlabel` require `--ack-irreversible` because they can permanently remove, overwrite, or broadly change contacts. `contacts update` requires the current `contact.revision`, and bulk commands return Wix bulk jobs that can be checked with `contacts get-bulk-job`.
- `form-schemas list`, `get`, `query`, `count`, deleted-form reads, provider configs, and summaries are live reads in this boundary.
- `form-schemas create`, `bulk-create`, `update`, `clone`, `bulk-clone`, and `restore` are reviewed-plan writes.
- `form-schemas delete`, `bulk-delete`, `remove-from-trash`, and `bulk-remove-deleted-field` require `--ack-irreversible` because they move schemas to trash or permanently remove schemas or deleted fields.
- `chat-settings get` and `query` are live reads for Wix Forms AI chat settings.
- `chat-settings create` and `update` are reviewed-plan writes. `update` requires the current `chatSettings.revision`.
- `chat-settings delete` requires `--ack-irreversible` because it removes AI chat settings for a form. Official docs say the Wix Forms app must be installed and the chat settings ID matches the form ID.
- `interactive-form-sessions generate-summary` is a non-mutating helper for Developer Preview Wix Interactive Form Sessions.
- `interactive-form-sessions create`, `create-streamed`, `send-message`, and `send-message-streamed` are reviewed-plan writes because an interactive session can collect and submit form data when the official `dryRun` body field is false.
- Streamed Interactive Form Sessions commands request the official `text/event-stream` response and return JSON when possible or raw response text when Wix streams events.
- `intake-forms query` and `create-customer-submission-link` are reads/helpers. `archive`, `unarchive`, and `update-expiration-period` are reviewed-plan writes. `delete` also requires `--ack-irreversible` because Wix deletes the underlying form and orphaned submissions are hidden from the submissions API.
- `intake-form-submissions query`, `search`, `count-by-intake-form-ids`, and `list-data-by-contacts` are reads/helpers. `cancel`, `extend`, `exempt`, and `delete` are reviewed-plan writes. `cancel` and `delete` also require `--ack-irreversible`; canceled submissions cannot be reactivated.
- `community-groups list`, `get`, `get-by-slug`, and `query` are live reads for Wix Community Groups.
- `community-groups create` and `update` are reviewed-plan writes. Official docs say only group admins can update groups and that group visibility changes can approve or reject pending join requests.
- `community-groups delete` requires `--ack-irreversible` because it removes a community group. Official docs say list and query return up to 100 groups, secret groups are visible only to admins and members, and group creation may become a pending create request depending on the site's dashboard setting.
- `community-group-rules list` reads rules for one community group. `community-group-rules create-or-replace` is a reviewed-plan replacement write and requires `--ack-irreversible` because official docs say it replaces all existing rules when rules already exist. Group Rules Updated is callback-only.
- `community-group-requests list` and `query` read group creation requests across a site. `community-group-requests approve` and `reject` are reviewed-plan writes and require `--ack-irreversible` because they decide site-member requests to create groups. Group Request Approved and Group Request Rejected are callback-only.
- `community-group-members list`, `list-memberships`, `query`, and `query-memberships` read group member or membership records. `community-group-members add` and `remove` are reviewed-plan writes and require `--ack-irreversible` because they change group membership. Member Added and Member Removed are callback-only.
- `community-group-roles assign` and `unassign` are reviewed-plan writes and require `--ack-irreversible` because they change group permissions. Official docs say assigning overrides the current `role.value`, unassigning only supports `ADMIN`, and Role Assigned/Unassigned events are callback-only.
- `community-join-requests list` and `query` read join requests for one private group. `community-join-requests approve` and `reject` are reviewed-plan writes and require `--ack-irreversible` because they decide pending private-group membership. Join Group Request Approved and Rejected are callback-only.
- `community-membership-questions list` reads a group's membership questions, and `list-answers` reads submitted answers by explicit official `memberIds` and `paging` inputs. `community-membership-questions create-or-replace` is a reviewed-plan replacement write and requires `--ack-irreversible` because it replaces the full question set; `--questions-json` must be Wix's official object with a `questions` array, and an empty questions array removes all questions.
- `community-comments get`, `query`, `count`, `list-by-resource`, and `get-thread` read comment records, counts, resource lists, or threads. `community-comments create` and `update` are reviewed-plan writes. `community-comments delete`, `moderate-draft-content`, `mark`, `unmark`, `hide`, `publish`, and all bulk commands require `--ack-irreversible` because they change public moderation state, move comments, or delete comment content. Comment moderation events are callback-only.
- `community-reports get`, `query`, and `count-by-reason-types` read Reports V2 records and counts. Official docs say Reports V2 is currently supported for Wix Comments only. `community-reports create`, `update`, and `upsert` are reviewed-plan writes. `community-reports delete` and `bulk-delete-by-filter` require `--ack-irreversible` because official docs say they remove reports from the dashboard report list, and bulk delete can remove multiple reports.
- `community-reviews get`, `query`, and `count` read Reviews records and counts. Official docs say Reviews is currently only available with the `stores` namespace. `community-reviews create`, `update`, and `set-reply` are reviewed-plan writes. `community-reviews delete`, `bulk-create`, `bulk-delete`, `remove-reply`, `update-moderation-status`, and `bulk-update-moderation-status` require `--ack-irreversible` because they delete review content or replies, change moderation/publication state, or affect multiple reviews.
- `community-review-requests get`, `query`, and `count` read review request records and counts. Official docs say Review Requests is currently only available with the `stores` namespace. `community-review-requests create` is a reviewed-plan write. `community-review-requests delete` and `bulk-cancel-by-filter` require `--ack-irreversible` because delete removes canceled requests and bulk cancel starts an async job that can cancel multiple review requests.
- `community-moderation-rules get`, `query`, and `check-content` read rules or return moderation actions for submitted content. `community-moderation-rules create`, `update`, and `delete` are reviewed-plan writes and require `--ack-irreversible` because moderation rules automate how newly submitted comments or reviews are approved, rejected, or sent for manual approval.
- `inbox-conversations get` reads one Inbox conversation, and `get-or-create` is a reviewed-plan write because it can create a conversation for a participant. `inbox-messages list` reads messages, and `send` is a reviewed-plan write that requires `--ack-irreversible` because it sends a message and can send notifications.
- `email-subscriptions query` is a live read/helper for Developer Preview Wix Email Subscriptions. Official docs currently support querying by `email` with the `$in` array filter.
- `email-subscriptions upsert`, `bulk-upsert`, and `generate-unsubscribe-link` are reviewed-plan writes. Official docs say the unsubscribe link changes status only if the recipient uses the link.
- Email Subscriptions methods require `Manage Email Subscriptions`; Email Subscription Changed is callback-only and not a CLI command.
- `contact-labels query`, `contact-labels list`, and `contact-labels get` are live reads in this boundary.
- `contact-labels query`, `contact-labels list`, and `contact-labels get` are shipped with app/user identity auth and permission `Manage Contact Labels`.
- `contact-labels find-or-create`, `contact-labels update`, and `contact-labels delete` are reviewed-plan writes.
- `contact-labels delete` requires `--ack-irreversible` and is verified by label read-back absence (`404`).
- `contact-labels find-or-create` can create a new label; `update` verifies by reread.
- `contact-labels delete` removes the label from contacts and triggers label-related events.
- `contact-extended-fields get`, `contact-extended-fields list`, and `contact-extended-fields query` are live reads in this boundary.
- `contact-extended-fields find-or-create`, `contact-extended-fields update`, and `contact-extended-fields delete` are reviewed-plan writes.
- `contact-extended-fields delete` requires `--ack-irreversible` because Wix says deleting an extended field permanently deletes any contact data stored in that field.
- `contact-notes get` and `contact-notes query` are live reads in this boundary.
- `contact-notes create`, `contact-notes update`, and `contact-notes delete` are reviewed-plan writes.
- `contact-notes delete` requires `--ack-irreversible` because it removes a saved note from the contact history. Official docs say notes must belong to an existing contact, note text is capped at 2048 characters, and updates require the current note revision.
- `contact-attachments get` and `contact-attachments list` are live reads in this boundary.
- `contact-attachments generate-upload-url` and `contact-attachments delete` are reviewed-plan writes.
- `contact-attachments delete` requires `--ack-irreversible` because it removes a saved file attachment from the contact. Official docs say attachments belong to a contact ID and upload URL creation works with the Upload API.
- `crm-tasks get`, `crm-tasks query`, and `crm-tasks count` are live reads/helpers in this boundary.
- `crm-tasks create`, `crm-tasks update`, `crm-tasks move-after`, and `crm-tasks delete` are reviewed-plan writes. `crm-tasks delete` also requires `--ack-irreversible` because it removes a CRM task. Official docs say task query defaults to `createdDate DESC`, update requires the existing task revision, count can filter tasks, and move-after can place a task first when `beforeTaskId` is omitted. Task Created, Task Deleted, Task Overdue, and Task Updated are callback-only events.
- `crm-pipelines get` and `crm-pipelines query` are live Developer Preview reads/helpers in this boundary.
- `crm-pipelines create`, `crm-pipelines update`, `crm-pipelines bulk-update-tags`, `crm-pipelines bulk-update-tags-by-filter`, and `crm-pipelines delete` are Developer Preview reviewed-plan writes. `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`; delete permanently removes a pipeline, and filtered tag updates can affect every pipeline when no filter is sent. Official docs say update requires the current pipeline revision and the filtered tag update returns an async job ID. Pipeline Created, Pipeline Deleted, and Pipeline Updated are callback-only events.
- `crm-cards get`, `crm-cards query`, `crm-cards search`, and `crm-cards search-by-stage` are live Developer Preview reads/helpers in this boundary.
- `crm-cards create`, `crm-cards update`, `crm-cards bulk-update-tags`, `crm-cards bulk-update-tags-by-filter`, `crm-cards move`, and `crm-cards delete` are Developer Preview reviewed-plan writes. `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`; delete permanently removes a card, and filtered tag updates can affect every card in a pipeline when no filter is sent. Official docs say update requires the current card revision, move stays inside one pipeline, and the filtered tag update returns an async job ID. Card Assigned, Card Created, Card Deleted, Card Moved, Card Overdue, Card Stale, and Card Updated are callback-only events.
- AI Site-Chat commands cover Widget Settings, Widget Settings V2, Conversations, and Messages. Conversations and visitor-scoped Messages methods require site visitor or site member identity. `ai-site-chat-messages bulk-create` is a reviewed-plan write requiring `--ack-irreversible` because it sends chat messages. V1 Widget Settings commands are kept with Wix's October 25, 2026 deprecation warning.
- `create-submission`, `update-submission`, `confirm-submission`, and `bulk-mark-submissions-as-seen` are reviewed-plan writes in this tool.
- `delete-submission` is destructive and requires `--ack-irreversible` with live apply.
- `bulk-mark-submissions-as-seen` requires `--all-unseen` for empty ID requests.
- `update-submission` includes explicit revision checks.
- `confirm-submission` is only valid for `PENDING` submissions.
- `data-collections` reads are live reads. `data-collections create`, `update`, `patch`, `create-field`, `update-field`, `patch-field`, `add-plugin`, and `delete-plugin` are reviewed-plan writes. `data-collections delete` and `data-collections delete-field` also need `--ack-irreversible`. `data-collections delete-field` can remove values from existing items across the collection, `data-collections add-plugin` and `data-collections delete-plugin` can change collection behavior broadly, and `data-collections patch` stays narrow to `displayName`, `displayField`, and `permissions`.
- All `data-collections` writes use Wix app or Wix user identity auth and require `Manage Data Collections`.
- `data-collections` writes verify by collection reread where the method supports it.
- `data-indexes list` is a live read.
- `data-indexes create` and `data-indexes drop` are reviewed-plan writes.
- All `data-indexes` writes use Wix app or Wix user identity auth and require `Manage Data Indexes`.
- Official Wix docs say Wix Data APIs require the site code editor to be enabled.
- `data-indexes create` and `drop` are async state changes, so this wrapper verifies by rereading the index list and checking index status instead of claiming an immediate final result.
- This wrapper refuses dropping `SYSTEM` indexes when current readback proves the index is system-generated.
- `data-folders get` is a live read. Omitting `--folder-id` returns the root folder.
- `data-folders create`, `update`, `delete`, `create-collection-reference`, and `delete-collection-reference` are reviewed-plan writes.
- `data-folders delete` requires `--ack-irreversible`.
- All `data-folders` writes use Wix app or Wix user identity auth and require `Manage Data Collections`.
- Official Wix docs say only the root folder may contain other folders, and the root folder cannot be updated or deleted.
- `data-extension-schemas list` is a read command in this boundary and requires an explicit FQDN.
- `data-extension-schemas create`, `update`, and `delete-user-defined-fields` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `data-extension-schemas delete-user-defined-fields` also requires `--ack-irreversible`.
- This family uses Wix app or Wix user identity auth in the site context and keeps schema-plugin setup separate from the API write flow.
- `data-extension-schemas` writes verify by rereading the schema list for the same FQDN and checking that user-defined fields are gone after delete.
- `data-folders create` and `update` verify by rereading the folder after apply.
- `data-folders create-collection-reference` and `delete-collection-reference` verify by rereading collection references for the same collection name.
- `data-folders delete` verifies by expecting folder read-back `404` and keeps the manual-only recovery limit explicit because Wix moves collection references back to the root folder.
- `data-items save`, `truncate`, `bulk-remove`, `bulk-save`, `bulk-update`, `bulk-insert-references`, and `bulk-remove-references` are reviewed-plan writes.
- `data-items truncate` and `bulk-remove` also need `--ack-irreversible`.
- `data-items save` and `bulk-save` are upsert writes and do not promise rollback.
- `data-items bulk-save` refuses live apply for items without explicit IDs unless `--return-entity` is enabled for safe verification.
- `data-items bulk-update` is full-object replacement and every item must include `id`.
- `data-items bulk-insert-references` and `bulk-remove-references` verify through official `is-referenced` readback and refuse obvious no-op apply runs.
- `data-permissions get` and `data-permissions get-my` are live reads.
- `data-permissions update`, `data-permissions add-special`, `data-permissions update-special`, and `data-permissions remove-special` are reviewed-plan writes.
- All `data-permissions` writes use Wix app or Wix user identity auth and require `Manage Data Collections`.
- Official Wix docs say this family only applies to collections created in the CMS or through the Data Collections API. Wix app collections, shared collections, and external collections are excluded from this family.
- `data-permissions add-special` and `update-special` require exactly one of `--user-id` or `--policy-id`.
- `data-permissions update-special` is replace-style in official docs, so this wrapper requires all four special access flags explicitly.
- `data-permissions update-special` and `remove-special` also require `--data-collection-id` in this tool so apply can verify with official `get-permissions` readback instead of trusting the write response alone.
- Wix app collections are reference-only in official docs and do not create a separate CLI command family. Use `data-collections list|get` and `data-items get|query|search` with official app collection IDs such as `Stores/Products`, `Bookings/Services`, and `Events/Events`. App collections are system collections with fixed permissions and read-only fields managed by the relevant Wix business app.
- `events-settings get` is a live read for Wix Events & Tickets app settings. `events-settings update` is a reviewed-plan write and is Developer Preview in official Wix docs. Official docs say the Wix Events & Tickets app must be installed, the family requires `Manage Events`, and most settings are read-only except specific payment-related settings.
- `portfolio-settings get` is a live read for Wix Portfolio app settings. `portfolio-settings update` is a reviewed-plan write. Official docs say the Wix Portfolio app must be installed, each site has one settings record created automatically when the app is installed, the family requires `Manage Portfolio`, update requires the current `revision`, and Portfolio Settings Created is a webhook/event surface.
- `portfolio-collections list`, `get`, and `query` are live reads/helpers for Wix Portfolio collections. `portfolio-collections create` and `update` are reviewed-plan writes, and `delete` is an irreversible reviewed-plan write. Official docs say the Wix Portfolio app must be installed, query returns up to `100` collections with default sort `id ASC`, update requires the current `revision`, and Collection Created/Updated/Deleted are webhook/event surfaces. Current read/event pages show an unrelated-looking permission label, `Wix Multilingual - Nile Wrapper Domain Events Read`, so this wrapper keeps that docs mismatch explicit.
- `portfolio-projects list`, `get`, and `query` are live reads/helpers for Wix Portfolio projects. `portfolio-projects create`, `update`, and `bulk-update` are reviewed-plan writes, and `delete` is an irreversible reviewed-plan write. Official docs say the Wix Portfolio app must be installed, cover images and videos must first be uploaded or imported through Wix Media Manager, query returns up to `100` projects with default sort `id ASC`, update requires the current `revision`, and Project Created/Updated/Deleted are webhook/event surfaces. The official bulk update page currently renders `/portfolio/projects/projects/api/v1/bulk/portfolio/projects/update`, so this wrapper keeps that path oddity explicit.
- `portfolio-project-items list` and `get` are live reads/helpers for project items in existing Wix Portfolio projects. `portfolio-project-items create`, `update`, `bulk-create`, `bulk-update`, and `duplicate` are reviewed-plan writes, while `delete` and `bulk-delete` are irreversible reviewed-plan writes. Official docs say the Wix Portfolio app must be installed, project items belong to existing projects, images and videos must first be uploaded or imported through Wix Media Manager, and Project Item Created/Updated/Deleted are webhook/event surfaces. Current get/list/event pages show an unrelated-looking permission label, `Wix Multilingual - Nile Wrapper Domain Events Read`, and several write pages omit a clear auth block, so this wrapper keeps that docs mismatch explicit.
- `suppliers-hub-products get`, `query`, `search`, and `query-categories` are live reads/helpers. `create`, `update`, `bulk-create`, `bulk-update`, `bulk-add-to-store`, and `bulk-update-tags` are reviewed-plan writes, while `delete`, `bulk-delete`, and `bulk-update-tags-by-filter` are stronger reviewed-plan writes. Official docs mark this API Developer Preview and say access requires approved Wix business-partner agreement. Keep the `query` versus `search` consistency difference, async `jobId` note for filtered tag updates, empty-filter all-product risk, callback-only product events, and Bulk Add Products To Store endpoint mismatch explicit.
- `suppliers-hub-suppliers get` and `query` are live reads. `create`, `update`, `bulk-create`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes, while `delete`, `bulk-delete`, and `bulk-update-tags-by-filter` are stronger reviewed-plan writes. Official docs mark this API Developer Preview and say access requires approved Wix business-partner agreement. Supplier `update` and `bulk-update` require the current supplier `revision`; keep the before-state revision guard, async `jobId` note for filtered tag updates, empty-filter all-supplier risk, and callback-only supplier events explicit.
- `suppliers-hub-marketplace-provider-submissions submit-generated-mockups` is a reviewed-plan provider-backend reporting write. Official docs mark this API Developer Preview, cap each submission at 100 mockups, and say Wix keys each result by authenticated provider, `providerProductId`, and `imageType`. Keep the generated endpoint versus curl example mismatch explicit.
- `events-v3 get`, `query`, `count-by-status`, `get-by-slug`, and `list-by-category` are live reads/helpers for Wix Events & Tickets events. `list-by-category` is Developer Preview in official Wix docs.
- Use the exact command `events-v3 list-by-category` when checking the Developer Preview category listing method.
- `events-v3 create`, `update`, `clone`, and `publish-draft` are reviewed-plan writes.
- `events-v3 cancel`, `bulk-cancel-by-filter`, `delete`, and `bulk-delete-by-filter` are reviewed-plan writes that also require `--ack-irreversible` because cancellation closes registration and can send notifications, while deletion leaves GDPR access request as the documented retrieval path.
- Official Wix Events V3 docs say Wix Events & Tickets must be installed, reads use `Read Events`, and writes use `Manage Events`.
- `events-ticket-definitions-v3 get`, `query`, and `count` are live reads/helpers for Wix Events ticket definitions.
- `events-ticket-definitions-v3 create`, `update`, and `reorder` are reviewed-plan writes. `update` requires the current `ticketDefinition.revision`.
- `events-ticket-definitions-v3 delete`, `bulk-delete-by-filter`, and `change-currency` are reviewed-plan writes that also require `--ack-irreversible` because they can affect event ticket sales, paid-ticket accounting, or many ticket definitions at once.
- Official Wix Ticket Definitions V3 docs say Wix Events & Tickets must be installed, callable methods require `Manage Ticket Definitions`, and Orders API generates tickets after purchase.
- `events-categories get` and `query` are live reads/helpers for Wix Events categories.
- `events-categories create`, `bulk-create`, `update`, `assign-events`, `bulk-assign-events`, and `reorder-events` are reviewed-plan writes.
- `events-categories delete`, `unassign-events`, and `bulk-unassign-events` are reviewed-plan writes that also require `--ack-irreversible` because they remove category records or event/category relationships.
- Official Wix Events Categories docs say Wix Events & Tickets must be installed and category methods require `Manage Events`.
- `events-schedule-items get`, `list`, `query`, and `list-bookmarks` are live reads/helpers for Wix Events schedule items and current-member bookmarks.
- `events-schedule-items add`, `update`, `publish-draft`, `reschedule-draft`, `create-bookmark`, and `delete-bookmark` are reviewed-plan writes.
- `events-schedule-items delete` and `discard-draft` are reviewed-plan writes that also require `--ack-irreversible` because they remove draft schedule content or clear all draft schedule changes.
- Official Wix Events Schedule Items docs say Wix Events & Tickets must be installed, each event has one published schedule and one draft schedule, and schedule item methods require `Manage Events`.
- `events-policies-v2 get` and `query` are live reads/helpers for Wix Events policy records.
- `events-policies-v2 create`, `update`, and `reorder` are reviewed-plan writes.
- `events-policies-v2 delete` is a reviewed-plan write that also requires `--ack-irreversible` because it permanently deletes the policy.
- Official Wix Events Policies V2 docs say Wix Events & Tickets must be installed, each event can have up to 3 policies, reads use `Read Policies`, writes use `Manage Policies`, and update requires the current policy `revision`.
- `events-staff-members get` and `query` are live reads/helpers for Wix Events staff member records.
- `events-staff-members create` and `update` are reviewed-plan writes.
- `events-staff-members update` requires the current `staffMember.revision`.
- `events-staff-members query` supports the official query defaults unless the request body overrides them.
- `events-staff-members delete` is a reviewed-plan write that also requires `--ack-irreversible` because it permanently removes the staff member from the staff member list.
- Official Wix Events Staff Members docs say Wix Events & Tickets must be installed, methods require `Manage Events - all permissions`, and query defaults to `createdDate ASC` with paging limit `100` and offset `0`.
- `events-guests query` is a live read/helper for Wix Events guest records.
- Official Wix Event Guests docs say Wix Events & Tickets must be installed, guest details require the `guestDetails` fieldset, Query Event Guests requires `Read Event Tickets and Guest List`, and query defaults to `createdDate ASC` with paging limit `100` and offset `0`.
- `events-rsvps-v2 get`, `query`, `search`, `count`, and `list-summary` are live reads/helpers for RSVP records and summaries.
- Use `events-rsvps-v2 list-summary` with one or more `--event-id` values to read RSVP summary counts.
- `events-rsvps-v2 create`, `update`, `bulk-update`, and `check-in` are reviewed-plan writes; `delete`, `bulk-delete-by-filter`, and `cancel-check-in` also require `--ack-irreversible`.
- Official Wix Events RSVP V2 docs say Wix Events & Tickets must be installed. Reads require `Read Event Tickets and Guest List`; create requires `Manage Events`; update, delete, bulk actions, check-in, and cancel check-in require `Manage Guest List`. Update and bulk update require RSVP revisions, bulk update accepts up to `100` RSVPs, check-in and cancel check-in accept up to `11` guests, query defaults to `createdDate ASC` with paging limit `100` and offset `0`, and RSVP created/updated/deleted pages are webhook/event surfaces rather than CLI commands.
- `events-ticket-reservations get` is a live read/helper for one Wix Events ticket reservation.
- `events-ticket-reservations create` and `bulk-update-tags` are reviewed-plan writes; `delete`, `bulk-update-tags-by-filter`, and `cancel` also require `--ack-irreversible`.
- Official Wix Events Ticket Reservations docs say Wix Events & Tickets must be installed. Create/get/cancel require `Events Checkout`, delete and bulk tag updates require `Manage Orders`, create starts a `PENDING` reservation that auto-expires, `ticketReservation.tickets` supports 1-50 line items, known-ID bulk tag updates use `ids` for up to `100` reservations, by-filter bulk tag updates are asynchronous and an empty filter updates all reservations, delete cannot be undone, cancel cannot be restored, and Ticket Reservation created/deleted/updated pages are webhook/event surfaces rather than CLI commands.
- `events-tickets get` and `list` are live reads/helpers for generated event tickets.
- `events-tickets update`, `bulk-update`, and `check-in` are reviewed-plan writes; `delete-check-in` also requires `--ack-irreversible` because it removes attendance check-in evidence.
- Official Wix Events Tickets docs say Wix Events & Tickets must be installed, tickets are generated by the Orders API, get/list require `Read Event Tickets and Guest List`, write methods require `Manage Guest List`, list returns up to `100` tickets, batch methods use the official `ticketNumber` array with a local `100`-ticket cap, and Order Updated is a webhook/event surface rather than a CLI command.
- `events-orders list`, `get`, `get-summary`, `get-checkout-options`, `list-available-tickets`, `query-available-tickets`, and `get-invoice` are live reads/helpers for event orders and checkout pricing/ticket availability.
- Use `events-orders query-available-tickets` to read available ticket inventory through the official checkout query helper.
- `events-orders update`, `bulk-update`, and `update-checkout` are reviewed-plan writes; `confirm`, `create-reservation`, `cancel-reservation`, and `checkout` also require `--ack-irreversible`.
- Official Wix Events Orders docs say Wix Events & Tickets must be installed, paid checkout requires a premium plan plus at least one configured payment method, order reads require `Read Basic Events Order Info`, order writes require `Manage Orders`, checkout methods require `Events Checkout`, Confirm Order can mark eligible orders `PAID` and send ticket confirmation email, Checkout can create orders and contacts and affect payment/ticket inventory, `query-available-tickets` uses max `limit` `1000` and min `offset` `0`, the old checkout reservation endpoints are deprecated, and order/deprecated reservation pages are webhook/event surfaces rather than CLI commands.
- `events-forms get-form` is a live read/helper for one event registration form.
- `events-forms add-control` and `update-control` are reviewed-plan writes; `discard-draft`, `delete-control`, `update-messages`, and `publish-draft` also require `--ack-irreversible`.
- Official Wix Events Form docs say Wix Events & Tickets must be installed, `get-form` requires `Read Events`, write methods require `Manage Events` and Wix app or Wix user identity, name and email controls are required and pinned to the top of the form, add/update/delete control changes can automatically trigger form publishing, `discard-draft` and `publish-draft` are deprecated, and Form Event Updated is a webhook/event surface rather than a CLI command.
- `restaurants-menus list`, `get`, and `query` are live reads/helpers for Wix Restaurants menu records.
- `restaurants-menus create`, `update`, `bulk-create`, `bulk-update`, `duplicate`, and `update-extended-fields` are reviewed-plan writes; `delete` also requires `--ack-irreversible`.
- Official Wix Restaurants Menus docs say the Wix Restaurants Menus app must be installed, the family is Developer Preview, writes use `Manage Restaurants - all permissions`, update and bulk update require the current menu revision, list/query can return up to `500` menus, rendered pages use `/restaurants/menus-menu/v1` public paths while markdown schema also exposes `/restaurants/menus/v1`, and Menu Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-sections list`, `get`, and `query` are live reads/helpers for Wix Restaurants menu section records.
- `restaurants-sections create`, `update`, `bulk-create`, `bulk-update`, and `duplicate` are reviewed-plan writes; `delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix Restaurants Sections docs say the Wix Restaurants Menus app must be installed, the family is Developer Preview, methods use `Manage Restaurants - all permissions`, update and bulk update require the current section revision, list/query can return up to `500` sections, rendered pages use `/restaurants/menus-section/v1` public paths while markdown schema also exposes `/restaurants/menus/v1`, reusing one section across multiple menus can break Wix site functionality, and Section Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-items list`, `get`, `query`, `search`, and `count` are live reads/helpers for Wix Restaurants menu item records.
- `restaurants-items create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes; `delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix Restaurants Items docs say the Wix Restaurants Menus app must be installed, methods use `Manage Restaurants - all permissions`, update and bulk update require the current item revision, list returns up to `500` items, search defaults to `paging.limit` `500`, `paging.offset` `0`, and `createdDate` ascending, count can count all items when no filter is sent, bulk update handles up to `100` items, rendered pages use `/restaurants/menus-item/v1` public paths while markdown schema also exposes `/restaurants/menus/v1`, current rendered method pages do not show a stable method-level Developer Preview marker for this Items slice, and Item Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-item-labels list`, `get`, and `query` are live reads/helpers for Wix Restaurants item-label records.
- `restaurants-item-labels create` and `update` are reviewed-plan writes; `delete` also requires `--ack-irreversible`.
- Official Wix Restaurants Item Labels docs say the Wix Restaurants Menus app must be installed, the family is Developer Preview, rendered pages use `/restaurants/item-labels/v1` public paths, create/update/delete use `Manage Restaurants - all permissions`, current rendered get/list/query pages show `Wix Multilingual - Nile Wrapper Domain Events Read`, update requires the current label revision, list/query can return up to `500` labels, and Item Label Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-item-variants list`, `get`, `query`, and `count` are live reads/helpers for Wix Restaurants item-variant records.
- `restaurants-item-variants create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes; `delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix Restaurants Item Variants docs say the Wix Restaurants Menus app must be installed, the family is Developer Preview, rendered pages use `/restaurants/item-variants/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require the current variant revision, list/query can return up to `500` variants, count can count all variants when no filter is sent, bulk update returns up to `100` item variants, and Item Variant Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-item-modifiers list`, `get`, `query`, and `count` are live reads/helpers for Wix Restaurants item-modifier records.
- `restaurants-item-modifiers create`, `restaurants-item-modifiers update`, `restaurants-item-modifiers bulk-create`, and `restaurants-item-modifiers bulk-update` are reviewed-plan writes; `restaurants-item-modifiers delete` and `restaurants-item-modifiers bulk-delete` also require `--ack-irreversible`.
- Official Wix Restaurants Item Modifiers docs say the Wix Restaurants Menus app must be installed, the family is Developer Preview, rendered pages use `/restaurants/item-modifiers/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require the current modifier revision, list/query can return up to `500` modifiers, count can count all modifiers when no filter is sent, and Item Modifier Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-item-modifier-groups list`, `get`, `query`, and `count` are live reads/helpers for Wix Restaurants item-modifier-group records.
- `restaurants-item-modifier-groups create`, `restaurants-item-modifier-groups update`, `restaurants-item-modifier-groups bulk-create`, and `restaurants-item-modifier-groups bulk-update` are reviewed-plan writes; `restaurants-item-modifier-groups delete` also requires `--ack-irreversible`.
- Official Wix Restaurants Item Modifier Groups docs say the Wix Restaurants Menus app must be installed, the family is Developer Preview, rendered pages use `/restaurants/item-modifier-group/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require the current modifier group revision, list/query can return up to `500` modifier groups, count can count all modifier groups when no filter is sent, bulk create accepts up to `100` modifier groups, bulk update can return up to `100` modifier groups, the official bulk update page renders `/restaurants/item-modifier-group/v1/bulk/modifiers-groups/update`, and Item Modifier Group Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-online-order-operation-groups get` and `query` are live reads/helpers for Wix Restaurants Online Orders operation groups.
- `restaurants-online-order-operation-groups create`, `update`, `bulk-create`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes; `delete`, `bulk-delete`, and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix Restaurants Online Orders Operation Groups docs say the Wix Restaurants Orders app must be installed, methods use `Manage Restaurants - all permissions`, update and bulk update require current operation group revisions, deleting an operation group deletes its operations, `bulk-update-tags-by-filter` is async and can update all operation groups when no filter is sent, and Operation Group Created/Updated/Deleted are webhook/event surfaces rather than CLI commands.
- `restaurants-online-order-operations get`, `list`, `query`, availability calculations, and `validate-address` are live reads/helpers for Wix Restaurants Online Orders operations.
- `restaurants-online-order-operations update` and `bulk-update-tags` are reviewed-plan writes; `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix Restaurants Online Orders Operations docs say the Wix Restaurants Orders app must be installed, current rendered pages show Developer Preview and `/restaurants-operations/v1` public paths, methods use `Manage Restaurants - all permissions`, update requires the current operation revision, operations are automatically created from operation groups and locations, and `bulk-update-tags-by-filter` is async and can update all operations when no filter is sent.
- `restaurants-online-order-menu-ordering-settings get`, `query`, and `list-menus-availability-status` are live reads/helpers for Wix Restaurants Online Orders menu ordering settings.
- `restaurants-online-order-menu-ordering-settings update`, `bulk-update`, `bulk-update-tags`, `update-extended-fields`, and `upsert-by-menu-id` are reviewed-plan writes; `bulk-update-tags-by-filter` also requires `--ack-irreversible`.
- Official Wix Restaurants Online Orders Menu Ordering Settings docs say the Wix Restaurants Orders app and Wix Restaurants Menus app must be installed, current rendered pages show Developer Preview and `/menu-ordering-settings/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require current revisions, menu ordering settings are created automatically for each menu, `bulk-update-tags-by-filter` is async and can update all menu ordering settings when no filter is sent, and Menu Ordering Settings Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-online-order-fulfillment-methods list`, `get`, `query`, `list-available-for-address`, `get-accumulated-availability`, `get-combined-availability`, and `get-aggregated-availability` are live reads/helpers for Wix Restaurants Online Orders fulfillment methods.
- `restaurants-online-order-fulfillment-methods create`, `bulk-create`, `update`, and `bulk-update-tags` are reviewed-plan writes; `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix Restaurants Online Orders Fulfillment Methods docs say the Wix Restaurants Orders app must be installed, current rendered pages show Developer Preview and `/fulfillment-methods/v1` public paths, methods use `Manage Restaurants - all permissions`, update requires the current revision, Get Accumulated Fulfillment Methods Availability and Get Combined Method Availability are deprecated, and Fulfillment Method Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-online-order-availability-exceptions get` and `query` are live reads/helpers for Wix Restaurants Online Orders availability exceptions.
- `restaurants-online-order-availability-exceptions create`, `bulk-create`, `update`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes; `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix Restaurants Online Orders Availability Exceptions docs say the Wix Restaurants Orders app must be installed, each availability exception requires an operation ID, current rendered pages show Developer Preview and `/restaurants-availability-exceptions/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require current revisions, and Availability Exception Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-online-order-service-fees calculate`, `list`, `get`, and `query` are live reads/helpers for Wix Restaurants Online Orders service fee rules.
- `restaurants-online-order-service-fees create`, `bulk-create`, `update`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes; `delete`, `bulk-delete`, and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix Restaurants Online Orders Service Fees docs say the Wix Restaurants Orders app must be installed, current rendered pages show Developer Preview and `/service-fees/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require current rule revisions, `bulk-update-tags-by-filter` is async and can update all rules when no filter is sent, and Rule Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-online-order-notification-recipients get` and `query` are live reads/helpers for Wix Restaurants Online Orders notification recipients.
- `restaurants-online-order-notification-recipients create`, `bulk-create`, `update`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes; `delete`, `bulk-delete`, and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix Restaurants Online Orders Notification Recipients docs say the Wix Restaurants Orders app must be installed, current rendered pages show Developer Preview and `/rest-notification-recipients/v1` public paths, methods use `Manage Restaurants - all permissions`, update and bulk update require current recipient revisions, broad tag-by-filter changes can affect many recipients, and Recipient Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-reservations get`, `list`, `query`, and `search` are live reads/helpers for Wix Restaurants Reservations.
- `restaurants-reservations create`, `update`, `bulk-archive`, `bulk-unarchive`, `create-held`, and `reserve` are reviewed-plan writes; `delete` and `cancel` also require `--ack-irreversible`.
- Official Wix Restaurants Reservations docs say the Wix Table Reservations app must be installed and at least 1 business location configured, current rendered pages show Developer Preview and `/table-reservations/reservations/v1` public paths, `update` requires the current reservation revision, `create-held` reservations expire after 10 minutes, `reserve` converts held reservations to `RESERVED` or `REQUESTED`, `delete` only deletes `HELD` reservations, archived reservations cannot be updated until unarchived, and Reservation Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-reservation-locations get`, `list`, and `query` are live reads/helpers for Wix Restaurants Reservation Locations.
- `restaurants-reservation-locations update` is a reviewed-plan write and requires the current `reservationLocation.revision`.
- Official Wix Restaurants Reservation Locations docs say the Wix Table Reservations app must be installed, current rendered pages show Developer Preview and `/table-reservations/reservation-locations/v1` public paths, reservation locations can only be created and archived through the Dashboard or Locations API, and Reservation Location Created/Updated are webhook/event surfaces rather than CLI commands.
- `restaurants-reservation-time-slots check`, `get-scheduled`, and `get` are live reads/helpers for Wix Restaurants Reservation Time Slots availability.
- Official Wix Restaurants Reservation Time Slots docs say the Wix Table Reservations app must be installed and at least 1 business location configured, current rendered pages show Developer Preview and `/table-reservations/reservations/v1` public paths, `check` uses `Manage Reservations (Medium)`, `get-scheduled` and `get` use `Manage Reservations (Basic)`, scheduled slots follow the reservation location `businessSchedule`, nearby slots can be requested with `slotsBefore` and `slotsAfter`, and time slot responses can show `AVAILABLE`, `UNAVAILABLE`, or `NON_WORKING_HOURS`.
- `restaurants-reservation-experiences get`, `query`, `search`, and `get-by-slug` are live reads/helpers for Wix Restaurants Experiences.
- `restaurants-reservation-experiences create`, `update`, and `bulk-update-tags` are reviewed-plan writes; `bulk-update-tags-by-filter` also requires `--ack-irreversible`.
- Official Wix Restaurants Experiences docs say the Wix Table Reservations app must be installed and at least 1 reservation location configured, current rendered pages show Developer Preview and `/table-reservations/experiences/v1` public paths, `update` requires the current `experience.revision`, broad tag updates by filter can affect many experiences, and Experience Created/Tags Modified/Updated are webhook/event surfaces rather than CLI commands.
- `blog-posts-stats get`, `query`, `list`, `get-by-slug`, `get-metrics`, `get-total`, and `query-count` are live reads/helpers for published Wix Blog posts and post stats.
- Use `blog-posts-stats get-total` for the official total published posts stat.
- Official Wix Blog Posts & Stats docs say these methods use `Read Blog`, query/list return up to `100` posts, query/list default to `firstPublishedDate` descending with pinned posts first, `paging.limit` `50`, and `paging.offset` `0`, and Post Created/Deleted/Liked/Unliked/Updated are webhook/event surfaces rather than CLI commands.
- `blog-draft-posts get`, `query`, `list`, `get-deleted`, and `list-deleted` are live reads/helpers for Wix Blog draft posts and trashed draft posts.
- `blog-draft-posts create`, `update`, `delete`, `bulk-create`, `bulk-update`, `bulk-delete`, `publish`, `remove-from-trash-bin`, and `restore-from-trash-bin` are reviewed-plan writes; `delete --permanent`, `bulk-delete`, and `remove-from-trash-bin` also require `--ack-irreversible`.
- Official Wix Blog Draft Posts docs say these methods require Wix app or Wix user authentication and `Manage Blog`; draft posts have a `400KB` size limit; third-party app creates require `memberId`; unknown category IDs are silently omitted; query/list return up to `100` draft posts and default to `editedDate DESC`, `paging.limit` `50`, and `paging.offset` `0`; publishing creates or updates the published post; Draft Deleted/Created/Updated are webhook/event surfaces rather than CLI commands.
- `blog-categories get`, `query`, `list`, and `get-by-slug` are live reads/helpers for Wix Blog categories.
- `blog-categories create` and `update` are reviewed-plan writes; `delete` is a reviewed-plan write that also requires `--ack-irreversible`.
- Official Wix Blog Categories docs say create/update/delete require Wix app or Wix user authentication and `Manage Blog`; reads require `Read Blog`; sites can have up to `100` categories per language and up to `10` categories per post; query/list default to `paging.limit` `50` and `paging.offset` `0`; `list` sorts by `displayPosition DESC` and cannot be overridden; Category Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `blog-tags get`, `query`, `get-by-label`, and `get-by-slug` are live reads/helpers for Wix Blog tags.
- `blog-tags create` is a reviewed-plan write; `delete` is a reviewed-plan write that also requires `--ack-irreversible`.
- Official Wix Blog Tags docs say create/delete require Wix app or Wix user authentication and `Manage Blog`; reads require `Read Blog`; a post can have up to `30` tags; query returns up to `500` tags and defaults to `postCount DESC`, `paging.limit` `50`, and `paging.offset` `0`; deleting a tag removes it from every blog post that contains it; Tag Created/Deleted/Updated are webhook/event surfaces rather than CLI commands.
- `blog-likes get` and `query` are live reads/helpers for likes created by the currently authenticated site visitor or member through the API.
- `blog-likes create` is a reviewed-plan write; `delete` and `delete-by-fqdn-entity-id` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix Blog Likes docs say the Wix Blog app must be installed, create/delete require visitor or member authentication and `Manage Blog`, reads require `Read Blog`, blog post likes use FQDN `wix.blog.v3.post`, query returns up to `100` current-user API-created likes and defaults to `createdDate DESC`, `paging.limit` `50`, and `paging.offset` `0`; Like Created/Deleted are Developer Preview webhook/event surfaces rather than CLI commands.
- Forum is intentionally disabled: official Wix docs say Forum APIs were deprecated on October 15, 2025 and Wix Forum was discontinued on March 1, 2026, after which forum data was deleted. Do not call or invent `forum-*` commands; use Groups API for migration work.
- `data-sharing list-policies`, `get-policy`, and `list-shared-collections` are live reads.
- `data-sharing create-policy`, `update-policy`, and `connect` are reviewed-plan writes.
- `data-sharing delete-policy` and `disconnect` are reviewed-plan writes that also require `--ack-irreversible`.
- All `data-sharing` methods use Wix app or Wix user identity auth and require `Manage Data Collection Sharing`.
- Official Wix docs say Data Sharing only works between sites in the same Wix account, external collections and Wix App collections cannot be shared, collection permissions remain unchanged, `update-policy` can only change `dataItemsFilter`, and updates automatically apply to connected sites.
- Deleting a sharing policy disconnects all associated connections and can break target-site code. Disconnecting removes the current site's local view of the shared collection.
- Mention that account-level site reads use `WIX_API_KEY` and `WIX_ACCOUNT_ID`.
- Mention that `accounts get` and `accounts list-child-accounts` use the same account-level auth path and are contract-gated in the official Accounts docs.
- Mention that `contributors query`, `contributors remove`, and `contributors change-role` use Wix app or Wix user identity for the current installed site and need the `Manage Contributors` permission.
- Mention that `contributors change-contributor-location` uses the same auth path, but the official method page currently lists permission `SITE_ROLES.CHANGE_LOCATION` with scope text `View SEO Settings: SCOPE.PROMOTE.VIEW-SEO`.
- Mention that `contributors remove` is dry-run first, requires `--account-id` and `--site-id`, and only applies with `--apply --yes --ack-irreversible`.
- Mention that `contributors change-role` is dry-run first, requires `--account-id`, `--site-id`, and explicit role GUIDs in `--role-ids-json`, and only applies with `--apply --yes`.
- Mention that `contributors change-role` replaces all existing role assignments for that contributor and verifies apply with provider `newAssignedRoles` plus readback query, not perfect role-state proof.
- Mention that `contributors change-contributor-location` is dry-run first, requires `--account-id`, `--site-id`, and explicit location GUIDs in `--location-ids-json`, and only applies with `--apply --yes`.
- Mention that `contributors change-contributor-location` replaces all existing location assignments for that contributor's role assignments and verifies apply with provider `newAssignedLocations` plus readback query, not perfect full location-state proof.
- Mention that the nearby `Get Roles Info` discovery API is beta-gated and is `excluded`.
- Mention that location lookup is `excluded` from the Contributors surface and that official Wix docs point callers to the Locations API for location GUIDs.
- Mention that `analytics-data get` uses Wix app or Wix user identity auth, is read-only, requires `Site Analytics - read permissions`, and follows the documented recent 62-day data window.
- Mention that `analytics-sessions get-list-job-result`, `list-async`, `mark-recordings-deleted`, and `mark-session-recorded` use Wix app or Wix user identity auth, require `Manage Session Recording Analytics - all permissions`, and are select-beta-only in official Wix docs. `list-async` is a reviewed-plan named async job starter. The two recording-state mutation commands require `--ack-irreversible`.
- Mention that `analytics-semantic-models list`, `get`, and `query` use the same site-context auth path, are read-only, require `Site Analytics - read permissions`, and keep Wix's required `interval` query rule explicit.
- Mention that `automation-storage-items create`, `get`, `query`, `bulk-update-tags`, `bulk-update-tags-by-filter`, `update-counter-by`, and `update-value` use Wix app or Wix user identity auth, require `Set Up Automations`, and keep the 100-item cap, immutable key/type boundary, and no-delete-method boundary explicit. `bulk-update-tags-by-filter` is a reviewed-plan write requiring `--ack-irreversible` because an empty filter can update all storage items.
- Mention that `automations-v2 create`, `get`, `update`, `delete`, `query`, and `validate` use Wix app or Wix user identity auth and require `Set Up Automations`. `validate` is a safe preflight helper, while create, update, and delete are reviewed-plan writes requiring `--ack-irreversible` because they can activate, change, or remove site workflows.
- Mention that `async-jobs get` and `list-items` use the same site-context auth path, are read-only, require `READ ASYNC JOBS`, and keep the no-generic-jobs-runner boundary explicit.
- Mention that `branches get-default`, `branches get`, and `branches query` use the same site-context auth path, are read-only, require `Manage Site Branches`, and only manage branch metadata.
- Mention that `ai-credits get-balance` uses `WIX_API_KEY` only, sends `Authorization` only, is read-only, and is live-unverified because the official intro says the balance scope can vary by caller access.
- Mention that shipped `site-actions bulk-delete`, `site-actions duplicate`, and `site-actions publish` use the same account-level auth path family. `site-actions bulk-delete` requires `--ack-irreversible` for apply, while `site-actions duplicate` and `site-actions publish` do not.
- Mention that `projects create-project` uses the same account-level auth path and supports `--apply --yes`, `--plan-out`, `--plan-in`, and `--receipt-out` with response-only success proof.
- Mention that `site-folders` uses the same account-level auth path and is marked as API-key-only beta access in the official docs.
- Mention that `projects create-project` in this boundary is `WIX`-only via local guardrail, and `--name` is required before apply.
- Mention that Account Level Sites Skills is docs-only and non-callable. The official `Query Sites` recipe maps to the shipped `sites query` command. The official `Create Site from Template` recipe combines template search, project/site creation, optional publish, and optional Headless OAuth App creation; do not invent a `sites-skills` command.
- Mention that most non-account-level families depend on app context and installed-app scope using `WIX_APP_ID`, `WIX_APP_SECRET`, and `WIX_INSTANCE_ID`.
- Mention that `site-actions publish` is dry-run first, uses `POST /site-publisher/v1/site/publish`, requires `--apply --yes`, supports `--plan-out`, `--plan-in`, and `--receipt-out`, refuses stale `--plan-in` apply plans, and is considered successful only after re-reading the site with `published=true`.
- Mention that `domains check-availability` and `domains suggest` use account-level auth (`WIX_API_KEY` + `WIX_ACCOUNT_ID`) and are read-only.
- Mention that `domain-dns get-zone` and `domain-dns preview-zone` use the same account-level auth path, stay read-only, and require `--domain-name`.
- Mention that `domain-dns create-zone`, `domain-dns update-zone`, and `domain-dns delete-zone` use the same account-level auth path and are reviewed-plan writes.
- Mention that `domain-dns delete-zone` always requires `--ack-irreversible`, `domain-dns update-zone` requires `--ack-irreversible` when record deletions are requested, and `domain-dns create-zone` requires `--ack-irreversible` when replacing an existing zone.
- Mention that `dns-propagation get` is a read-only account-level DNS propagation status command and uses `--dns-propagation-id` (the domain name including TLD in Wix docs).
- Mention that Domain DNS docs say the family is account-API-key only, Wix caps records at 50 values per type, and update methods are nameserver-gated for external domains connected by nameservers to Wix sites.
- Mention that official domain-search pages show `Authorization: <AUTH>` in REST examples and `ApiKeyStrategy` in SDK examples; this wrapper uses the repo’s account-level resolver and does not use a generic request bridge.
- Mention that connected-domains (`connected-domains list`, `connected-domains get`, `connected-domains get-setup-info`, `connected-domains create`, `connected-domains delete`) use account-level auth in this tool (`Authorization` + `wix-account-id`).
- Mention that `connected-domains create` is dry-run first, requires `--apply --yes`, supports `--plan-out`, `--plan-in`, and `--receipt-out`, and this tool requires `--site-id` so the target site is explicit.
- Mention that `connected-domains delete` is dry-run first, requires `--apply --yes --ack-irreversible`, supports `--plan-out`, `--plan-in`, and `--receipt-out`, and can remove DNS records or make a site fall back to its free Wix URL.
- Mention that connected-domains SDK examples still show `ApiKeyStrategy`, so the auth mismatch is tracked in docs and this boundary stays explicit and live-unverified.
- Mention that Business Management methods (`analytics-data`, `analytics-semantic-models`, `async-jobs`, `branches`, `site-search`, `locations`, `tags`, `site-properties`, `cookie-consent-policy`, `dashboard-favorite-list`, `site-urls`, `benefit-items`, `balances`, `coupons`, `gift-cards`) are in the implemented command surface and use app-token auth (`WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID`) unless local token path commands are active.
- Mention that `bookings-reader-v2 query-extended-bookings` and `bookings-reader-v2 count-extended-bookings` are read-only and live-unverified, need the Wix Bookings app, use `Read bookings calendar - including participants`, `Manage Bookings`, and `Read Bookings - Including Participants`, do not expose a get-by-id method, default `query` to `id ASC` with `cursorPaging.limit 50`, cap `query` at `100`, keep course bookings on `scheduleId`, treat `withBookingAllowedActions` as optional, and require UTC date filters.
- Mention that `bookings-writer-v2 get-multi-service`, `get-multi-service-availability`, `bulk-calculate-allowed-actions`, `bulk-get-multi-service-allowed-actions`, `get-anonymous-action-token`, `get-anonymous`, and `get-service-anonymous` are reads/helpers and remain live-unverified. Mention that other `bookings-writer-v2` commands are reviewed-plan writes. Mention that `cancel`, `decline`, `reschedule`, `update-participants`, `bulk-confirm-or-decline`, `remove-from-multi-service`, `cancel-multi-service`, `decline-multi-service`, `reschedule-multi-service`, `cancel-anonymous`, and `reschedule-anonymous` also require `--ack-irreversible`. Keep the Wix Bookings app prerequisite, official `12`-booking bulk-create limit, Time Slots V2 pre-check guidance, 2-8 sequential appointment rule for multi-service bookings, anonymous-token credential warning, Reader V2 read boundary, and separate Attendance/payment-flow boundaries explicit.
- Mention that `bookings-services-v2 get`, `query`, `search`, `count`, `query-policies`, `query-locations`, `query-categories`, `validate-slug`, and `list-add-on-groups-by-service-id` are live reads/helpers and remain live-unverified. Mention that `bookings-services-v2 create`, `update`, `bulk-create`, `bulk-update`, `bulk-update-by-filter`, `enable-pricing-plans`, `set-custom-slug`, `clone`, `create-add-on-group`, and `update-add-on-group` are reviewed-plan writes. Mention that `bookings-services-v2 delete`, `bulk-delete`, `bulk-delete-by-filter`, `set-service-locations`, `disable-pricing-plans`, `delete-add-on-group`, and `set-add-ons-for-group` are reviewed-plan writes that also require `--ack-irreversible`. Keep the Wix Bookings app prerequisite, `Manage Bookings` write permission, create-service required fields, appointment capacity/staff rule, `100`-service bulk limit, location replacement risk, pricing-plan removal risk, and callback-only service events explicit.
- Mention that `bookings-resources-v2 get`, `query`, `search`, and `count` are live reads/helpers and remain live-unverified. Mention that `bookings-resources-v2 create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes. Mention that `bookings-resources-v2 delete` and `bulk-delete` are reviewed-plan writes that also require `--ack-irreversible` because Wix cancels resource schedules during deletion. Keep the Wix Bookings app prerequisite, `Read Bookings - Public Data` read permission, `Manage Bookings` write permission, create `resource.name` requirement, update `resource.revision` requirement, `50`-resource bulk limit, staff-resource warning, and Resource Types V2 separation explicit.
- Mention that `bookings-resource-types-v2 get`, `query`, and `count` are live reads/helpers and remain live-unverified. Mention that `bookings-resource-types-v2 create` and `update` are reviewed-plan writes. Mention that `bookings-resource-types-v2 delete` is a reviewed-plan write that also requires `--ack-irreversible` because Wix deletes all connected resources. Keep the Wix Bookings app prerequisite, `Read Bookings - Public Data` read permission, `Read Bookings Calendar` get-method note, `Manage Bookings` write permission, create `resourceType.name` requirement, update `resourceType.revision` requirement, staff-resource-type warning, and Resources V2 separation explicit.
- Mention that `bookings-staff-members get`, `query`, `search`, `count`, `get-deleted`, and `list-deleted` are live reads/helpers and remain live-unverified. Mention that `bookings-staff-members create`, `update`, `assign-working-hours-schedule`, `bulk-update-tags`, `bulk-update-tags-by-filter`, `connect-to-user`, and `disconnect-from-user` are reviewed-plan writes. Mention that `bookings-staff-members delete` and `remove-from-trash` are reviewed-plan writes that also require `--ack-irreversible`. Keep the Wix Bookings app prerequisite, `BOOKINGS.STAFF_MEMBER_READ` read permission, `Manage Bookings` write permission, `staffMember.revision` update requirement, `100`-staff bulk tag limit, async job note for filter tag updates, and Wix-managed staff-resource warning explicit.
- Mention that `bookings-policies get`, `query`, `count`, and `strictest` are live reads/helpers and remain live-unverified. Mention that `bookings-policies create` and `update` are reviewed-plan writes. Mention that `bookings-policies delete` and `set-default` are reviewed-plan writes that also require `--ack-irreversible`. Keep the Wix Bookings app prerequisite, `Read Bookings - Public Data` read permission, `Manage Bookings Services and Settings` write permission, `bookingPolicy.revision` update requirement, default-policy deletion restriction, daylight-saving policy-window warning, and query default of `createdDate ASC` with `cursorPaging.limit 100` explicit.
- Mention that `bookings-policy-snapshots list` is a live read/helper and remains live-unverified. Keep the Wix Bookings app prerequisite, `Read Bookings - Public Data` permission, booking-ID lookup shape, one-snapshot-per-booking-with-related-eCommerce-order rule, no-snapshot-for-bookings-without-related-eCommerce-order rule, no-create-snapshot rule, and Booking Policy Service Plugin Developer Preview service-plugin boundary explicit.
- Mention that `bookings-attendance get`, `query`, and `count` are live reads/helpers and remain live-unverified. Mention that `bookings-attendance set` and `bulk-set` are reviewed-plan writes. Mention that `bookings-attendance delete` and `bulk-delete` are reviewed-plan writes that also require `--ack-irreversible`. Keep the Wix Bookings app prerequisite, `Read Bookings - Including Participants` read permission, `Manage Bookings` write permission, query booking/session perspectives, one-filter-per-query rule, query default of `id ASC` with `cursorPaging.limit 50`, `count` Developer Preview/member-auth-only limit, and Set Attendance validation warning explicit.
- Mention that `bookings-waitlist list` is a live read/helper and remains live-unverified. Mention that `bookings-waitlist register` is a reviewed-plan write requiring `--ack-event-session`. Mention that `bookings-waitlist leave` and `book` are reviewed-plan writes that require `--ack-event-session` and also require `--ack-irreversible`. Keep the Wix Bookings app prerequisite, Developer Preview status for all Waitlist methods, `type = EVENT` session limit, `Read Bookings - Public Data` read permission, `Manage Bookings` write permission, first-come-first-served suggestion order, `waitingResources` list shape, required `waitingResource`/`formInfo` registration request, `registrationId`/`waitingResource` leave request, and booking/enrollment side effects explicit.
- Mention that `calendar-schedules-v3 get` and `query` are live reads/helpers and remain live-unverified. Mention that `calendar-schedules-v3 create` and `update` are reviewed-plan writes. Mention that `calendar-schedules-v3 cancel` is a reviewed-plan write that also requires `--ack-irreversible` because Wix says cancelled schedules cannot be reactivated, updated, or assigned new events. Keep the Bookings-visible `schedule.appId` value `13d21c63-b5ec-5912-8397-c3a5ddb27a97`, current `schedule.revision` update requirement, active-by-default query behavior, supported filters `id`, `externalId`, `appId`, and `status`, and schedule-event callback-only boundary explicit.
- Mention that `calendar-schedule-time-frames-v3 get` and `list` are live read-only commands and remain live-unverified. Keep the one-to-100 schedule ID list limit, optional `timeZone`, no-update boundary, and Schedule Time Frame Updated callback-only boundary explicit.
- Mention that `calendar-events-v3 get`, `query`, `list`, `list-by-contact`, and `list-by-member` are live reads/helpers for Business Management Calendar events and remain live-unverified. State that this is separate from Wix Events & Tickets `events-v3`. Mention that `calendar-events-v3 create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes. Mention that `calendar-events-v3 cancel`, `bulk-cancel`, `restore-defaults`, and `split-recurring` are reviewed-plan writes that also require `--ack-irreversible`. Keep the create required fields, recurring master limits, `event.revision` update requirement, 100-ID list limit, 50-item bulk limit, contact/member date-window rule, and event callback-only boundary explicit.
- Mention that `calendar-event-views-v3 get` is a live read/helper and remains live-unverified. Keep the `GET /calendar/v3/events/view` path, current event view end-date/future-duration result, no event details boundary, one-year completeness rule, no manual extension or update boundary, and Events View Extended/Projection Updated callback-only boundary explicit.
- Mention that `calendar-participations-v3 get` and `query` are live reads/helpers and remain live-unverified. Mention that `calendar-participations-v3 create` and `update` are reviewed-plan writes and that `calendar-participations-v3 delete` is a reviewed-plan write requiring `--ack-irreversible`. Keep the event `participants` and `remainingCapacity` side effect, `participation.revision` update requirement, `partySize` 1-to-1000 rule, one-of `eventId` or `scheduleId` target rule, query default `createdDate DESC` with `cursorPaging.limit` 50, supported filters `id`, `eventId`, `scheduleId`, and `externalId`, Wix Bookings-managed participation warning, and participation event callback-only boundary explicit.
- Mention that Calendar Skills / default business hours is docs-only and non-callable. Do not expose or invent a `calendar-skills` command. Use the shipped `calendar-schedules-v3 query` and `calendar-events-v3 query|bulk-update|bulk-cancel|bulk-create` commands for the official default-business-hours recipe. Keep the Wix Bookings app prerequisite, universal business schedule external ID `4e0579a5-491e-4e70-a872-d097eed6e520`, mandatory existing `WORKING_HOURS` MASTER event query, duplicate-hours warning, and underlying Calendar Events V3 write gates explicit.
- Mention that Captcha is gated and non-callable in this REST CLI. Keep the Developer Preview Authorize method path `POST /captcharator/api/v1/authorize`, Wix site or Blocks app backend context, Wix reCAPTCHA element token requirement, and official Headless/REST-not-supported note explicit. Do not expose or invent `captcha authorize`.
- Mention that `bookings-external-calendars-v2 list-providers`, `list-connections`, `get-connection`, `list-calendars`, and `list-events` are live reads/helpers and remain live-unverified. Mention that `bookings-external-calendars-v2 connect-by-credentials`, `connect-by-oauth`, and `update-sync-config` are reviewed-plan writes. Mention that `connect-by-credentials` requires `--ack-external-credentials` and redacts secret fields in plans and receipts. Mention that `disconnect` is a reviewed-plan write that also requires `--ack-irreversible` because Wix says it deletes Wix calendar events from the external calendar. Keep the `Manage External Calendars` permission, provider connect-method choice, OAuth redirect flow, `from`/`to` or cursor requirement for `list-events`, `OWN_PI` fieldset rule for PI fields, partial-failure option, and legacy Bookings Calendar V1 compatibility-only boundary explicit.
- Mention that `bookings-service-options-v1 get`, `get-by-service-id`, and `query` are live reads/helpers and remain live-unverified. Mention that `bookings-service-options-v1 create`, `update`, and `clone` are reviewed-plan writes. Mention that `bookings-service-options-v1 delete` is a reviewed-plan write that also requires `--ack-irreversible` because Wix says deleting service options removes varied pricing from the service. Keep the single serviceOptionsAndVariants object per service limit, one-option-per-object limit, manual variant definition requirement, current `serviceOptionsAndVariants.revision` update requirement, query default of `id ASC` with `cursorPaging.limit 100`, and callback-only created/deleted/updated events explicit.
- Mention that course-specific Bookings flow is not a separate official REST family. Keep the combined shipped flow explicit: use `bookings-services-v2` for course service `schedule`, `defaultCapacity`, and `bookingPolicy.bookAfterStart`; `bookings-service-options-v1 get-by-service-id` for varied options; `bookings-reader-v2 query-extended-bookings` filtered by `bookedEntity.item.schedule.serviceId` to sum `attendance.numberOfAttendees`; and `bookings-writer-v2 create` with `booking.bookedEntity.schedule.scheduleId`. State that Time Slots V2 does not cover course availability and that Forms/checkout dependencies remain separate open rows.
- Mention that `donation-campaigns get`, `get-metrics`, and `query` are live reads, `donation-campaigns create`, `update`, `bulk-create`, `bulk-update`, `bulk-update-tags`, and `bulk-update-tags-by-filter` are reviewed-plan writes, the site must have Wix Donations installed, the current command set uses `Manage Donation Campaigns`, `query` defaults to `createdDate ASC` with `cursorPaging.limit 100`, `create` and `bulk-create` require `customAmountEnabled`, `predefinedDonationAmounts`, or both, campaign status is automatic, updates require the current `revision`, metrics are aggregated/default-currency only, `bulk-update-tags-by-filter` is async and verifies returned `jobId` only, and this boundary refuses empty-filter all-campaign retagging even though Wix allows it.
- Mention that `benefit-items get`, `list`, `query`, and `count` are live reads, `benefit-items create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes, `benefit-items delete`, `bulk-delete`, and `bulk-delete-by-filter` are destructive reviewed-plan writes requiring `--ack-irreversible`, sites using this API must install the Pricing Plans app, reads use `SCOPE.BENEFIT_PROGRAMS.READ (PII)`, writes use `Manage benefit programs` / `SCOPE.BENEFIT_PROGRAMS.MANAGE`, `query` defaults to paging limit `50`, `list` returns up to `1000` items, updates require the current `revision`, and this boundary refuses empty-filter bulk delete.
- Mention that `balances get`, `list`, and `query` are live reads, `balances change` and `balances revert-change` are reviewed-plan writes, sites using this API must install the Pricing Plans app, reads use `SCOPE.BENEFIT_PROGRAMS.READ (PII)`, writes use `Manage benefit programs`, `query` defaults to paging limit `50`, supported filters include `id`, `createdDate`, `beneficiary.memberId`, and `beneficiary.wixUserId`, and `revert-change` is a specific transaction undo path rather than a blanket rollback promise.
- Mention that `coupons get` and `coupons query` are live reads, `coupons create`, `coupons update`, and `coupons bulk-create` are reviewed-plan writes, `coupons delete` and `coupons bulk-delete` are irreversible reviewed-plan writes requiring `--ack-irreversible`, the site must have one of `stores`, `bookings`, `events`, or `pricingPlans` installed, all coupon methods use `Manage Coupons`, `query` is capped at `100`, coupon codes are case and space sensitive, and only one coupon can be applied per order.
- Mention that `loyalty-coupons get`, `query`, and `get-current-member` are live reads/helpers and remain live-unverified. Mention that `loyalty-coupons redeem-current-member`, `redeem`, and `delete` are reviewed-plan writes that also require `--ack-irreversible` because they redeem loyalty points or remove loyalty coupon records. Keep the Wix Loyalty Program prerequisite, loyalty-coupon-to-reference-coupon relationship, current-member auth boundary, and callback-only Coupon Created/Deleted events explicit.
- Mention that `loyalty-transactions get` and `query` are read-only and remain live-unverified. Keep the transaction activity types explicit: earn, redeem, adjust, refund, expire, and earn-attempt.
- Mention that `loyalty-social-media list` is a live read/helper and `loyalty-social-media create` is a reviewed-plan write requiring `--ack-irreversible` because following a channel can award loyalty points. Keep the visitor/member auth requirement, dashboard-enabled-channel prerequisite, and callback-only Followed Channel Created event explicit.
- Mention that `loyalty-imports get`, `query`, and `get-error-file-download-url` are live reads/helpers and remain live-unverified. Mention that `loyalty-imports create-file-url` is a reviewed-plan helper write without `--ack-irreversible`, while `loyalty-imports create` and `execute` are reviewed-plan writes that also require `--ack-irreversible` because imports can overwrite customer point balances. Keep the CSV, email column, points-balance column, 10MB max file size, row-level error behavior, and callback-only Loyalty Import Created event explicit.
- Mention that `gift-cards get`, `query`, `search`, and `count` are live reads, `gift-cards create`, `disable`, and `send-email` are reviewed-plan writes, `gift-cards disable` is irreversible and requires `--ack-irreversible`, the Wix Gift Card app must be installed, all shipped methods use `Manage eCommerce - all permissions`, `send-email` also needs a premium site plan, codes are obfuscated outside the create response, `count` is Developer Preview, and the deprecated list-by-email method is intentionally not shipped.
- Mention that `app-installation get-installed` is read-only, uses the current site/app token path, and redacts returned `appToken` values.
- Mention that `app-installation is-permitted` is a preflight helper, not a write.
- Mention that `app-installation install`, `app-installation install-from-share-url`, `app-installation uninstall`, `app-installation bulk-install`, and `app-installation bulk-uninstall` are reviewed-plan writes. They use `--plan-out`, then `--plan-in --apply --yes --ack-irreversible`, and recovery is manual because before-state snapshots are not guaranteed for arbitrary tenant context.
- Mention that the official App Installation pages say only logged-in Wix users or API key admins can use the API, and that the installed-app read page shows `Manage SEO Settings` while the install/uninstall pages show `Manage Events`, so this boundary keeps the mismatch explicit and stays live-unverified.
- Mention that `branches get-default`, `branches get`, and `branches query` are read-only, need permission `Manage Site Branches`, only manage branch metadata, and that `branches query` defaults to `updatedDate DESC` with `paging.limit 50` and `paging.offset 0` unless overridden.
- Mention that `site-search search` also uses the same site-context auth path, is read-only, needs permission `Read Site Documents`, and requires the Wix Site Search app to be installed on the site.
- Mention that `site-search search` accepts only the current official document types in this tool: `BLOG_POSTS`, `BOOKING_SERVICES`, `EVENTS`, `FORUM_CONTENT`, `ONLINE_PROGRAMS`, `PROGALLERY_ITEM`, and `STORES_PRODUCTS`.
- Mention that Wix Site Search docs currently show two REST URL shapes for the same method (`/_api/site-search/v1/search` on the main method page and example, `/v1/search` in the markdown schema). The wrapper should keep that mismatch explicit and follow the main method page path.
- Mention that `notifications notify` also follows app-token / user-identity site context, not account-key auth, and is bound by the above permissions and monthly-call limit note.
- Mention that these Business Management methods need plan-first writes where applicable and that `site-urls` remains read-only.

## Flag contract matrix

| Command or family | Read/live write state | Required flags for live write | Receipt / verification contract |
|---|---|---|---|
| pure reads (`auth check`, `contacts`, `members`, `app-installations`, `app-instance get`, `embedded-scripts get`, `custom-embeds list/get`, `secrets list|get-value`, `sender-emails list|get`, `sender-details list|get|get-default`, `sending-domains get|query`, `marketing-consent get|query|get-by-identifier`, `referral-program get|get-premium-features|get-ai-social-media-posts-suggestions`, `referral-rewards get|query`, `referring-customers get|query|get-by-referral-code`, `referred-friends get|query|get-by-contact-id`, `referral-tracker get|query|get-statistics`, `email-campaigns list|get|get-audience|list-statistics|list-recipients|identify-sender-address`, `donation-campaigns get|get-metrics|query`, `orders search|get`, `order-billing get-order-refundability|calculate-refund`, `benefit-items get|list|query|count`, `balances get|list|query`, `pricing-plans get|query|search|count`, `coupons get|query`, `gift-cards get|query|search|count`, `bookings-time-slots-v2 list-availability|get-availability|list-event|get-event|list-multi-service|get-multi-service`, `bookings-reader-v2 query-extended-bookings|count-extended-bookings`, `bookings-services-v2 get|query|search|count|query-policies|query-locations|query-categories|validate-slug|list-add-on-groups-by-service-id`, `bookings-resources-v2 get|query|search|count`, `bookings-resource-types-v2 get|query|count`, `bookings-staff-members get|query|search|count|get-deleted|list-deleted`, `calendar-schedules-v3 get|query`, `calendar-schedule-time-frames-v3 get|list`, `calendar-events-v3 get|query|list|list-by-contact|list-by-member`, `calendar-event-views-v3 get`, `calendar-participations-v3 get|query`, `campaign-validation validate-link|validate-html-links`, `events-settings get`, `portfolio-settings get`, `portfolio-collections get|query|list`, `portfolio-projects get|query|list`, `portfolio-project-items get|list`, `events-v3 get|query|count-by-status|get-by-slug|list-by-category`, `events-ticket-definitions-v3 get|query|count`, `events-categories get|query`, `events-schedule-items get|list|query|list-bookmarks`, `events-policies-v2 get|query`, `events-staff-members get|query`, `events-guests query`, `events-rsvps-v2 get|query|search|count|list-summary`, `events-ticket-reservations get`, `events-tickets get|list`, `events-orders list|get|get-summary|get-checkout-options|list-available-tickets|query-available-tickets|get-invoice`, `events-forms get-form`, `restaurants-menus list|get|query`, `restaurants-sections list|get|query`, `restaurants-items list|get|query|search|count`, `restaurants-item-labels list|get|query`, `restaurants-item-variants list|get|query|count`, `restaurants-item-modifiers list|get|query|count`, `restaurants-item-modifier-groups list|get|query|count`, `restaurants-online-order-operation-groups get|query`, `restaurants-online-order-operations get|list|query|first-available-time-slot-per-fulfillment-type|first-available-time-slots-per-operation|first-available-time-slots-per-menu|available-time-slots-for-date|available-dates-in-range|validate-address`, `restaurants-online-order-menu-ordering-settings get|query|list-menus-availability-status`, `restaurants-online-order-fulfillment-methods list|get|query|list-available-for-address|get-accumulated-availability|get-combined-availability|get-aggregated-availability`, `restaurants-online-order-availability-exceptions get|query`, `restaurants-online-order-service-fees calculate|list|get|query`, `restaurants-online-order-notification-recipients get|query`, `restaurants-reservations get|list|query|search`, `restaurants-reservation-locations get|list|query`, `restaurants-reservation-time-slots check|get-scheduled|get`, `restaurants-reservation-experiences get|query|search|get-by-slug`, `blog-posts-stats get|query|list|get-by-slug|get-metrics|get-total|query-count`, `blog-draft-posts get|query|list|get-deleted|list-deleted`, `blog-categories get|query|list|get-by-slug`, `blog-tags get|query|get-by-label|get-by-slug`, `market-listing search`, `editor-deep-link create`, `app-permissions list`, `contact-labels query`, `contact-labels list`, `contact-labels get`, `contact-extended-fields get|list|query`, `contact-notes get|query`, `contact-attachments get|list`, `data-indexes list`, `data-folders get`, `data-folders get-collection-references`, `data-permissions get/get-my`, `data-sharing list-policies|get-policy|list-shared-collections`, `form-submissions get-submission/query-submissions-by-namespace/count-submissions|get-media-upload-url`, `chat-settings get|query`, `interactive-form-sessions generate-summary`, `community-groups list|get|get-by-slug|query`, `email-subscriptions query`, `analytics-data get`, `analytics-semantic-models list|get|query`, `async-jobs get|list-items`, `branches get-default|get|query`, `site-search search`, `files list|get|batch-get|search|query|list-deleted|generate-upload-url|generate-resumable-upload-url|generate-download-url`, `media-folders list|get|search|query|list-deleted|generate-download-url`, `sites`, `domains`, `domain-dns get-zone|preview-zone`, `dns-propagation get`, `site-urls`, `accounts`, `contributors query`, `tags list|get`, `data-items get|query|count|aggregate|aggregate-pipeline|distinct|search|query-referenced|is-referenced`, `data-collections list|get`) | read-only | none | normal command output only |
| `referring-customers generate-for-contact` | reviewed-plan write | none | may create a referring customer for the provided contact ID or `me`; provider response plus reread |
| `referring-customers delete` | irreversible reviewed-plan write | `--ack-irreversible` | deletes a referring customer by ID and current revision query parameter |
| `referred-friends create` | reviewed-plan write | none | may create or return an existing referred friend for the current member identity and referral code; provider response plus reread |
| `referred-friends update` | reviewed-plan write | none | updates a referred friend using the official referredFriend object and current revision |
| `referred-friends delete` | irreversible reviewed-plan write | `--ack-irreversible` | deletes a referred friend by ID and current revision query parameter |
| Forum | disabled / non-callable | none | official docs say Forum was discontinued on March 1, 2026 and forum data was deleted; do not expose `forum-*` commands |
| `app-installation get-installed`, `app-installation is-permitted` | read-only | none | normal command output only |
| `blog-likes create` | plan-first write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider result plus readback when supported |
| `suppliers-hub-products get|query|search|query-categories` | read-only | none | normal command output only |
| `suppliers-hub-products delete`, `suppliers-hub-products bulk-delete`, `suppliers-hub-products bulk-update-tags-by-filter` | irreversible or broad async write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; before-state is captured when IDs are known; filtered tag updates verify async `jobId` creation |
| `suppliers-hub-products create|update|bulk-create|bulk-update|bulk-add-to-store|bulk-update-tags` | plan-first write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider response or readback for known IDs |
| `suppliers-hub-suppliers get|query` | read-only | none | normal command output only |
| `suppliers-hub-suppliers delete`, `suppliers-hub-suppliers bulk-delete`, `suppliers-hub-suppliers bulk-update-tags-by-filter` | irreversible or broad async write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; before-state is captured when IDs are known; filtered tag updates verify async `jobId` creation |
| `suppliers-hub-suppliers create|update|bulk-create|bulk-update|bulk-update-tags` | plan-first write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; update and bulk update read before-state and refuse stale supplier revisions |
| `suppliers-hub-marketplace-provider-submissions submit-generated-mockups` | plan-first provider reporting write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider response and bulkActionMetadata |
| plan-first Domain DNS writes (`domain-dns create-zone`, `domain-dns update-zone`, `domain-dns delete-zone`) | high-risk | `--plan-out`, then `--plan-in --apply --yes`, plus `--ack-irreversible` when required | receipt recommended with `--receipt-out`; verify by reread or `404` after delete |
| `contributors remove`, `connected-domains delete`, `locations archive`, `tags delete`, `secrets delete`, `sender-emails delete`, `sender-details delete`, `email-campaigns delete`, `pricing-plans delete`, `orders cancel`, `bookings-services-v2 delete`, `bookings-services-v2 bulk-delete`, `bookings-services-v2 bulk-delete-by-filter`, `bookings-services-v2 set-service-locations`, `bookings-services-v2 disable-pricing-plans`, `bookings-services-v2 delete-add-on-group`, `bookings-services-v2 set-add-ons-for-group`, `bookings-resources-v2 delete`, `bookings-resources-v2 bulk-delete`, `bookings-resource-types-v2 delete`, `bookings-staff-members delete`, `bookings-staff-members remove-from-trash`, `calendar-schedules-v3 cancel`, `calendar-events-v3 cancel`, `calendar-events-v3 bulk-cancel`, `calendar-events-v3 restore-defaults`, `calendar-events-v3 split-recurring`, `brands-v3 delete`, `brands-v3 bulk-delete`, `ribbons-v3 delete`, `ribbons-v3 bulk-delete`, `stores-info-sections-v3 delete`, `stores-info-sections-v3 bulk-delete`, `customizations-v3 delete`, `customizations-v3 remove-choices`, `customizations-v3 set-choices`, `order-billing capture-authorized-payments`, `order-billing void-authorized-payments`, `order-billing redeem-gift-card`, `order-billing refund-payments`, `benefit-items delete`, `benefit-items bulk-delete`, `benefit-items bulk-delete-by-filter`, `coupons delete`, `coupons bulk-delete`, `gift-cards disable`, `files bulk-delete`, `media-folders bulk-delete`, `site-actions bulk-delete`, `site-folders delete`, `data-items remove`, `data-collections delete`, `data-collections delete-field`, `data-folders delete`, `data-sharing delete-policy`, `data-sharing disconnect`, `portfolio-collections delete`, `portfolio-projects delete`, `portfolio-project-items delete`, `portfolio-project-items bulk-delete`, `events-v3 cancel`, `events-v3 bulk-cancel-by-filter`, `events-v3 delete`, `events-v3 bulk-delete-by-filter`, `events-ticket-definitions-v3 delete`, `events-ticket-definitions-v3 bulk-delete-by-filter`, `events-ticket-definitions-v3 change-currency`, `events-categories delete`, `events-categories unassign-events`, `events-categories bulk-unassign-events`, `events-schedule-items delete`, `events-schedule-items discard-draft`, `events-policies-v2 delete`, `events-staff-members delete`, `events-rsvps-v2 delete`, `events-rsvps-v2 bulk-delete-by-filter`, `events-rsvps-v2 cancel-check-in`, `events-ticket-reservations delete`, `events-ticket-reservations bulk-update-tags-by-filter`, `events-ticket-reservations cancel`, `events-tickets delete-check-in`, `events-orders confirm`, `events-orders create-reservation`, `events-orders cancel-reservation`, `events-orders checkout`, `events-forms discard-draft`, `events-forms delete-control`, `events-forms update-messages`, `events-forms publish-draft`, `restaurants-menus delete`, `restaurants-sections delete`, `restaurants-sections bulk-delete`, `restaurants-items delete`, `restaurants-items bulk-delete`, `restaurants-item-labels delete`, `restaurants-item-variants delete`, `restaurants-item-variants bulk-delete`, `restaurants-item-modifiers delete`, `restaurants-item-modifiers bulk-delete`, `restaurants-item-modifier-groups delete`, `restaurants-online-order-operation-groups delete`, `restaurants-online-order-operation-groups bulk-delete`, `restaurants-online-order-operation-groups bulk-update-tags-by-filter`, `restaurants-online-order-operations delete`, `restaurants-online-order-operations bulk-update-tags-by-filter`, `restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter`, `restaurants-online-order-fulfillment-methods delete`, `restaurants-online-order-fulfillment-methods bulk-update-tags-by-filter`, `restaurants-online-order-availability-exceptions delete`, `restaurants-online-order-availability-exceptions bulk-update-tags-by-filter`, `restaurants-online-order-service-fees delete`, `restaurants-online-order-service-fees bulk-delete`, `restaurants-online-order-service-fees bulk-update-tags-by-filter`, `restaurants-online-order-notification-recipients delete`, `restaurants-online-order-notification-recipients bulk-delete`, `restaurants-online-order-notification-recipients bulk-update-tags-by-filter`, `restaurants-reservations delete`, `restaurants-reservations cancel`, `restaurants-reservation-experiences bulk-update-tags-by-filter`, `blog-draft-posts bulk-delete`, `blog-draft-posts remove-from-trash-bin`, `blog-draft-posts delete --permanent`, `blog-categories delete`, `blog-tags delete`, `blog-likes delete`, `blog-likes delete-by-fqdn-entity-id` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify by readback/provider result |
| `calendar-participations-v3 delete` | irreversible participation write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify with participation or event reads when possible |
| `loyalty-coupons redeem-current-member`, `loyalty-coupons redeem`, `loyalty-coupons delete` | loyalty points or coupon record write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify by `get-current-member`, `query`, or `get` as appropriate |
| `loyalty-social-media create` | followed-channel loyalty write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | requires visitor/member auth; verify by `loyalty-social-media list` with the same identity |
| `loyalty-imports create-file-url` | loyalty import upload-url helper write | `--plan-out` for review, then `--plan-in --apply --yes` | use returned `filePath` and `uploadUrl` only for the official Loyalty Imports CSV upload flow |
| `loyalty-imports create`, `loyalty-imports execute` | loyalty points import write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify with `loyalty-imports get` and use `get-error-file-download-url` for failed rows |
| `contact-labels find-or-create`, `contact-labels update`, `contact-labels delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider result plus `404` absence for delete |
| `contact-extended-fields find-or-create`, `contact-extended-fields update`, `contact-extended-fields delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` also requires `--ack-irreversible`; receipt recommended with `--receipt-out` |
| `contact-notes create`, `contact-notes update`, `contact-notes delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` also requires `--ack-irreversible`; receipt recommended with `--receipt-out` |
| `contact-attachments generate-upload-url`, `contact-attachments delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` also requires `--ack-irreversible`; receipt recommended with `--receipt-out` |
| `cookie-consent-policy get-cookie-banner-settings|get-cmp-config|get-consent-config|query-consent-configs|list-apps-and-storage` | read/helper | none | normal command output only |
| `cookie-consent-policy update-cookie-banner-settings|update-cmp-config|create-consent-config|update-consent-config|bulk-create-consent-configs|bulk-update-consent-configs|bulk-update-consent-config-tags` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update-consent-config` requires current `consentConfig.revision`; `bulk-update-consent-configs` is Developer Preview; receipt recommended with `--receipt-out` |
| `cookie-consent-policy delete-consent-config|bulk-delete-consent-configs|bulk-update-consent-config-tags-by-filter` | irreversible or broad filtered write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; filtered tag updates may affect all consent configs when filter is empty |
| `dashboard-favorite-list get` | read | none | normal command output only |
| `dashboard-favorite-list create|update|add-favorite` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` requires current `favoriteList.revision`; receipt recommended with `--receipt-out` |
| `dashboard-favorite-list delete|delete-favorite` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | `delete-favorite` can delete the whole list when no favorites remain; receipt recommended with `--receipt-out` |
| `faq-category-v2 get|query|list` | read/helper | none | normal command output only |
| `faq-category-v2 create|update|update-extended-fields` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` requires current `category.revision`; receipt recommended with `--receipt-out` |
| `faq-category-v2 delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Deleting a category also deletes its question entries; receipt recommended with `--receipt-out` |
| `faq-question-entry-v2 list|get|query` | read/helper | none | normal command output only |
| `faq-question-entry-v2 create|update|bulk-update|set-labels|update-extended-fields` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` and `bulk-update` require current revisions; `set-labels` replaces all labels; receipt recommended with `--receipt-out` |
| `faq-question-entry-v2 delete|bulk-delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Question entry deletion is permanent; receipt recommended with `--receipt-out` |
| `functions-v1 get|query` | read/helper | none | normal command output only |
| `functions-v1 create|update|bulk-update-tags` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` requires current `function.revision`; receipt recommended with `--receipt-out` |
| `functions-v1 delete|bulk-update-tags-by-filter` | irreversible or broad filtered write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Delete permanently removes the function from the dashboard Function List; an empty filter can update all functions |
| `function-types get|query` | read/helper | none | normal command output only; query does not support filters or sorting |
| `function-templates get|query` | read/helper | none | normal command output only; query requires `appDefId` and `functionExtensionId` filters |
| `function-productions create|update` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Function Productions create or update a function together with its automation, service plugin configuration, and function method dependencies |
| `function-productions delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Delete removes the production and all associated entities |
| `builderless-productions get` | read/helper | none | normal command output only |
| `builderless-productions create|update` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Builderless Productions create ready-to-activate functions from templates with `formTemplateExtensionId`; update may have no effect after related entities are changed through other APIs |
| `function-methods query` | read/helper | none | normal command output only; query defaults to `createdDate DESC`, `paging.limit` 50, and `paging.offset` 0 |
| `function-methods create` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Creates a function method link; Wix recommends Function Productions or Builderless Productions for full function creation |
| `function-methods delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Deletes a function method link |
| `function-activations upsert|delete` | live execution write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Upsert publishes function logic live; delete deactivates the function |
| `function-spi-configurations get|query|validate` | read/helper | none | `validate` checks the configuration against the service plugin schema without creating it |
| `function-spi-configurations create|update` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` requires current `functionSpiConfiguration.revision`; reactivate the function to publish configuration changes |
| `function-spi-configurations delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Deletes a service plugin configuration |
| `billable-items get|query|search` | read/helper | none | `query` returns up to 1,000 items; `search` returns up to 100 items and is Developer Preview |
| `billable-items create|bulk-create|update|bulk-update|bulk-update-tags` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` requires current `billableItem.revision`; `create` and `bulk-update` are Developer Preview |
| `billable-items delete|bulk-delete|bulk-update-tags-by-filter` | irreversible or broad filtered write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Filtered tag updates are async and an empty filter updates all billable items |
| `payment-links get|query|search` | read/helper | none | Reads payment links by ID or by Wix query/search payloads |
| `payment-links initiate-payment|set-note|update-extended-fields|bulk-update-tags` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Initiate Payment creates a Wix eCommerce checkout and is not the normal payment link flow |
| `payment-links create|delete|activate|deactivate|send|bulk-update-tags-by-filter` | irreversible, customer-facing, or broad filtered write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Create locks payment values, send can notify up to 50 recipients, activation changes payment acceptance, and filtered tag updates can update all payment links |
| `payment-link-payments query|search` | read/helper | none | Reads payment records created from payment links |
| `payment-link-payments issue-receipt` | reviewed-plan receipt write | `--plan-out` for review, then `--plan-in --apply --yes` | Creates a Get Paid receipt; verify with provider response plus query/search readback for `receiptId` |
| `receipts get|query|get-latest-number` | read/helper | none | Reads receipts, searches receipts, or fetches the latest receipt number, optionally by prefix |
| `receipts regenerate-document|update-extended-fields` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Regenerate is for failed or stuck documents; extended fields updates do not increment revision |
| `receipts create|send-email` | irreversible or customer-facing receipt write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Receipts cannot be deleted after creation; send-email notifies customers |
| `receipt-presets get|list|get-default` | read/helper | none | Reads one preset, lists presets, or gets the default preset |
| `receipt-presets create|update|set-default|update-extended-fields` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `update` requires current `receiptPreset.revision`; set-default affects future receipt creation |
| `receipt-presets delete` | irreversible preset delete | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Permanently deletes the preset |
| `receipts-settings get` | read/helper | none | Reads the site's receipt numbering settings |
| `receipts-settings update` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Updates receipt numbering settings; requires current `receiptsSettings.revision`; verify with `receipts-settings get` |
| `payment-link-settings get` | read/helper | none | Reads the site's payment link checkout settings |
| `payment-link-settings update` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Updates payment link checkout settings; verify with `payment-link-settings get` |
| `headless-oauth-apps get|query` | read/helper | none | Reads one OAuth app or queries OAuth apps; query uses the official read-helper POST endpoint |
| `headless-oauth-apps create|update` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Creates or updates OAuth apps that authorize external Headless clients; update requires `oAuthApp.id` and `mask.paths` |
| `headless-authentication login-v2|retrieve-tokens` | sensitive auth helper | none | Logs in members or retrieves OAuth tokens while redacting passwords, codes, session tokens, access tokens, and refresh tokens from output |
| `headless-authentication register-v2|logout` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | Registers a member or terminates a member session; request and response secrets stay redacted |
| `headless-authentication change-password|sign-on` | irreversible sensitive auth write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Changes credentials or performs trusted sign-on that may create/update a member account; all secret fields stay redacted |
| `headless-recovery send-recovery-email` | irreversible email write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Sends a Wix-managed password-reset email; official docs require the connected site to be published and redirect URLs to be allowed authorization redirect URIs |
| `headless-redirects create-redirect-session` | irreversible visitor-flow write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | Creates a single-use URL for Wix-managed auth, logout, checkout, product, or booking flows; session tokens are redacted and official endpoint mismatch is documented |
| `headless-sitemap list-pages` | read-only | none | Lists Headless sitemap entries by official item type with cursor paging; official endpoint mismatch is documented |
| `headless-verification verify-during-authentication` | Developer Preview reviewed-plan auth write | `--plan-out` for review, then `--plan-in --apply --yes` | Submits an email verification code and state token during Headless authentication; code/token/session fields are redacted and official endpoint mismatch is documented |
| `crm-tasks create`, `crm-tasks update`, `crm-tasks move-after`, `crm-tasks delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` also requires `--ack-irreversible`; receipt recommended with `--receipt-out`; verify with `crm-tasks get` or `query` |
| `crm-pipelines create`, `crm-pipelines update`, `crm-pipelines bulk-update-tags`, `crm-pipelines bulk-update-tags-by-filter`, `crm-pipelines delete` | Developer Preview reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`; receipt recommended with `--receipt-out`; filtered tag updates return an async job ID |
| `crm-cards create`, `crm-cards update`, `crm-cards bulk-update-tags`, `crm-cards bulk-update-tags-by-filter`, `crm-cards move`, `crm-cards delete` | Developer Preview reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`; receipt recommended with `--receipt-out`; filtered tag updates return an async job ID |
| `ai-site-chat-widget-settings set`, `ai-site-chat-widget-settings-v2 update`, `ai-site-chat-messages bulk-create` | AI Site-Chat reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `bulk-create` also requires `--ack-irreversible`; receipt recommended with `--receipt-out`; verify with the related get/list command |
| `analytics-sessions list-async`, `analytics-sessions mark-recordings-deleted`, `analytics-sessions mark-session-recorded` | beta reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | recording-state mutations also require `--ack-irreversible`; receipt recommended with `--receipt-out`; `list-async` is a named async job starter only |
| `automation-storage-items create`, `automation-storage-items bulk-update-tags`, `automation-storage-items update-counter-by`, `automation-storage-items update-value` | Automations storage reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify with `automation-storage-items get` using `--consistent-read true` when needed |
| `automation-storage-items bulk-update-tags-by-filter` | irreversible filtered storage tag update | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | empty filter can update all storage items; provider returns a `jobId` |
| `automations-v2 create`, `automations-v2 update`, `automations-v2 delete` | irreversible automation workflow write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `automations-v2 validate` before create/update when possible; update requires current revision |
| `contacts create`, `contacts update`, `contacts delete`, `contacts merge`, `contacts label`, `contacts unlabel`, `contacts bulk-delete`, `contacts bulk-update`, `contacts bulk-label-unlabel` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete`, `merge`, and all bulk write jobs also require `--ack-irreversible`; receipt recommended with `--receipt-out` |
| `app-permissions create`, `app-permissions delete`, `contributors change-role`, `contributors change-contributor-location`, `connected-domains create`, `locations create`, `locations update`, `locations set-default`, `notifications notify`, `tags create`, `tags update`, `custom-embeds create`, `custom-embeds update`, `secrets create`, `secrets patch`, `sender-emails create`, `sender-emails get-or-create`, `sender-emails send-verification-code`, `sender-emails verify`, `sender-details create`, `sender-details update`, `sender-details mark-default`, `sending-domains authenticate`, `marketing-consent create`, `marketing-consent update`, `marketing-consent upsert`, `marketing-consent bulk-upsert`, `marketing-consent remove`, `referral-program activate`, `referral-program pause`, `referral-program generate-ai-social-media-posts-suggestions`, `referral-program update`, `email-campaigns publish`, `email-campaigns reuse`, `email-campaigns pause-scheduling`, `email-campaigns reschedule`, `email-campaigns send-test`, `events-settings update`, `portfolio-settings update`, `portfolio-collections create`, `portfolio-collections update`, `portfolio-projects create`, `portfolio-projects update`, `portfolio-projects bulk-update`, `portfolio-project-items create`, `portfolio-project-items update`, `portfolio-project-items bulk-create`, `portfolio-project-items bulk-update`, `portfolio-project-items duplicate`, `events-v3 create`, `events-v3 update`, `events-v3 clone`, `events-v3 publish-draft`, `events-ticket-definitions-v3 create`, `events-ticket-definitions-v3 update`, `events-ticket-definitions-v3 reorder`, `events-categories create`, `events-categories bulk-create`, `events-categories update`, `events-categories assign-events`, `events-categories bulk-assign-events`, `events-categories reorder-events`, `events-schedule-items add`, `events-schedule-items update`, `events-schedule-items publish-draft`, `events-schedule-items reschedule-draft`, `events-schedule-items create-bookmark`, `events-schedule-items delete-bookmark`, `events-policies-v2 create`, `events-policies-v2 update`, `events-policies-v2 reorder`, `events-staff-members create`, `events-staff-members update`, `events-rsvps-v2 create`, `events-rsvps-v2 update`, `events-rsvps-v2 bulk-update`, `events-rsvps-v2 check-in`, `events-ticket-reservations create`, `events-ticket-reservations bulk-update-tags`, `events-tickets update`, `events-tickets bulk-update`, `events-tickets check-in`, `events-orders update`, `events-orders bulk-update`, `events-orders update-checkout`, `events-forms add-control`, `events-forms update-control`, `restaurants-menus create`, `restaurants-menus update`, `restaurants-menus bulk-create`, `restaurants-menus bulk-update`, `restaurants-menus duplicate`, `restaurants-menus update-extended-fields`, `restaurants-items create`, `restaurants-items update`, `restaurants-items bulk-create`, `restaurants-items bulk-update`, `restaurants-item-labels create`, `restaurants-item-labels update`, `restaurants-item-variants create`, `restaurants-item-variants update`, `restaurants-item-variants bulk-create`, `restaurants-item-variants bulk-update`, `restaurants-item-modifiers create`, `restaurants-item-modifiers update`, `restaurants-item-modifiers bulk-create`, `restaurants-item-modifiers bulk-update`, `restaurants-item-modifier-groups create`, `restaurants-item-modifier-groups update`, `restaurants-item-modifier-groups bulk-create`, `restaurants-item-modifier-groups bulk-update`, `restaurants-online-order-operation-groups create`, `restaurants-online-order-operation-groups update`, `restaurants-online-order-operation-groups bulk-create`, `restaurants-online-order-operation-groups bulk-update`, `restaurants-online-order-operation-groups bulk-update-tags`, `restaurants-online-order-operations update`, `restaurants-online-order-operations bulk-update-tags`, `restaurants-online-order-menu-ordering-settings update`, `restaurants-online-order-menu-ordering-settings bulk-update`, `restaurants-online-order-menu-ordering-settings bulk-update-tags`, `restaurants-online-order-menu-ordering-settings update-extended-fields`, `restaurants-online-order-menu-ordering-settings upsert-by-menu-id`, `restaurants-online-order-fulfillment-methods create`, `restaurants-online-order-fulfillment-methods bulk-create`, `restaurants-online-order-fulfillment-methods update`, `restaurants-online-order-fulfillment-methods bulk-update-tags`, `restaurants-online-order-availability-exceptions create`, `restaurants-online-order-availability-exceptions bulk-create`, `restaurants-online-order-availability-exceptions update`, `restaurants-online-order-availability-exceptions bulk-update`, `restaurants-online-order-availability-exceptions bulk-update-tags`, `restaurants-online-order-service-fees create`, `restaurants-online-order-service-fees bulk-create`, `restaurants-online-order-service-fees update`, `restaurants-online-order-service-fees bulk-update`, `restaurants-online-order-service-fees bulk-update-tags`, `restaurants-online-order-notification-recipients create`, `restaurants-online-order-notification-recipients bulk-create`, `restaurants-online-order-notification-recipients update`, `restaurants-online-order-notification-recipients bulk-update`, `restaurants-online-order-notification-recipients bulk-update-tags`, `restaurants-reservations create`, `restaurants-reservations update`, `restaurants-reservations bulk-archive`, `restaurants-reservations bulk-unarchive`, `restaurants-reservations create-held`, `restaurants-reservations reserve`, `restaurants-reservation-locations update`, `restaurants-reservation-experiences create`, `restaurants-reservation-experiences update`, `restaurants-reservation-experiences bulk-update-tags`, `blog-draft-posts create`, `blog-draft-posts update`, `blog-draft-posts delete`, `blog-categories create`, `blog-categories update`, `blog-tags create`, `blog-draft-posts bulk-create`, `blog-draft-posts bulk-update`, `blog-draft-posts publish`, `blog-draft-posts restore-from-trash-bin`, `restaurants-sections create`, `restaurants-sections update`, `restaurants-sections bulk-create`, `restaurants-sections bulk-update`, `restaurants-sections duplicate`, `orders create`, `orders update`, `orders bulk-update`, `bookings-services-v2 create`, `bookings-services-v2 update`, `bookings-services-v2 bulk-create`, `bookings-services-v2 bulk-update`, `bookings-services-v2 bulk-update-by-filter`, `bookings-services-v2 enable-pricing-plans`, `bookings-services-v2 set-custom-slug`, `bookings-services-v2 clone`, `bookings-services-v2 create-add-on-group`, `bookings-services-v2 update-add-on-group`, `bookings-resources-v2 create`, `bookings-resources-v2 update`, `bookings-resources-v2 bulk-create`, `bookings-resources-v2 bulk-update`, `bookings-resource-types-v2 create`, `bookings-resource-types-v2 update`, `bookings-staff-members create`, `bookings-staff-members update`, `bookings-staff-members assign-working-hours-schedule`, `bookings-staff-members bulk-update-tags`, `bookings-staff-members bulk-update-tags-by-filter`, `bookings-staff-members connect-to-user`, `bookings-staff-members disconnect-from-user`, `calendar-schedules-v3 create`, `calendar-schedules-v3 update`, `calendar-events-v3 create`, `calendar-events-v3 update`, `calendar-events-v3 bulk-create`, `calendar-events-v3 bulk-update`, `brands-v3 create`, `brands-v3 update`, `brands-v3 bulk-create`, `brands-v3 bulk-update`, `brands-v3 get-or-create`, `brands-v3 bulk-get-or-create`, `ribbons-v3 create`, `ribbons-v3 update`, `ribbons-v3 bulk-create`, `ribbons-v3 bulk-update`, `ribbons-v3 get-or-create`, `ribbons-v3 bulk-get-or-create`, `stores-info-sections-v3 create`, `stores-info-sections-v3 update`, `stores-info-sections-v3 bulk-create`, `stores-info-sections-v3 bulk-update`, `stores-info-sections-v3 get-or-create`, `stores-info-sections-v3 bulk-get-or-create`, `customizations-v3 create`, `customizations-v3 update`, `customizations-v3 bulk-create`, `customizations-v3 bulk-update`, `customizations-v3 add-choices`, `customizations-v3 bulk-add-choices`, `order-billing authorize-charge-with-saved-payment-method`, `order-billing generate-receipts`, `donation-campaigns create`, `donation-campaigns update`, `donation-campaigns bulk-create`, `donation-campaigns bulk-update`, `donation-campaigns bulk-update-tags`, `donation-campaigns bulk-update-tags-by-filter`, `benefit-items create`, `benefit-items update`, `benefit-items bulk-create`, `benefit-items bulk-update`, `balances change`, `balances revert-change`, `pricing-plans create`, `pricing-plans update`, `pricing-plans bulk-update`, `coupons create`, `coupons update`, `coupons bulk-create`, `gift-cards create`, `gift-cards send-email`, `files update`, `files bulk-restore`, `files import`, `media-folders create`, `media-folders update`, `media-folders bulk-restore`, `site-properties update-business-contact`, `site-properties update-business-profile`, `site-properties update-business-schedule`, `site-properties update-consent-policy`, `projects create-project`, `site-actions duplicate`, `site-actions publish`, `site-folders create`, `site-folders update`, `site-folders move-folders`, `site-folders move-sites`, `data-items insert`, `data-items save`, `data-items update`, `data-items patch`, `data-items insert-reference`, `data-items remove-reference`, `data-items replace-references`, `data-items bulk-insert`, `data-items bulk-patch`, `data-items bulk-save`, `data-items bulk-update`, `data-items bulk-insert-references`, `data-items bulk-remove-references`, `data-collections create`, `data-collections update`, `data-collections patch`, `data-collections create-field`, `data-collections update-field`, `data-collections patch-field`, `data-collections add-plugin`, `data-collections delete-plugin`, `data-indexes create`, `data-indexes drop`, `data-folders create`, `data-folders update`, `data-folders create-collection-reference`, `data-folders delete-collection-reference`, `data-permissions update`, `data-permissions add-special`, `data-permissions update-special`, `data-permissions remove-special`, `data-sharing create-policy`, `data-sharing update-policy`, `data-sharing connect` | plan-first write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider result plus readback when supported |
| `calendar-participations-v3 create`, `calendar-participations-v3 update` | plan-first participation write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; update requires current `participation.revision` |
| `custom-embeds delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify by readback `404`, with manual-only recovery notes |
| `app-installation install`, `app-installation install-from-share-url`, `app-installation uninstall`, `app-installation bulk-install`, `app-installation bulk-uninstall` | plan-first write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify by provider result only, with manual recovery notes because before-state snapshots are not guaranteed for arbitrary tenant context |
| `data-items truncate`, `data-items bulk-remove` | irreversible reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | receipt recommended with `--receipt-out`; verify by count readback or item absence, with no rollback promise |
| `form-submissions create-submission`, `form-submissions update-submission`, `form-submissions delete-submission`, `form-submissions confirm-submission`, `form-submissions bulk-mark-submissions-as-seen` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider result, `ack-irreversible`, revision checks, and required preconditions |
| `chat-settings create`, `chat-settings update`, `chat-settings delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` also requires `--ack-irreversible`; `update` requires current `chatSettings.revision`; receipt recommended with `--receipt-out` |
| `community-group-rules create-or-replace` | irreversible replacement write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say existing rules are replaced |
| `community-group-requests approve`, `community-group-requests reject` | irreversible decision write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say only Wix users can approve or reject group requests |
| `community-group-members add`, `community-group-members remove` | irreversible membership write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say adding members can invite private members and removing members changes group membership |
| `community-group-roles assign`, `community-group-roles unassign` | irreversible role/permission write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say assigning overrides current `role.value` and unassigning only supports `ADMIN` roles |
| `community-join-requests approve`, `community-join-requests reject` | irreversible private-group membership decision | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say approval adds the site member to the private group |
| `community-membership-questions create-or-replace` | irreversible replacement write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say existing questions are replaced and an empty questions array removes all questions |
| `community-comments delete`, `community-comments moderate-draft-content`, `community-comments mark`, `community-comments unmark`, `community-comments hide`, `community-comments publish`, `community-comments bulk-publish`, `community-comments bulk-hide`, `community-comments bulk-delete`, `community-comments bulk-moderate-draft-content`, `community-comments bulk-move-by-filter` | irreversible comment moderation write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say delete removes comment content and bulk operations can affect multiple comments |
| `community-reports delete`, `community-reports bulk-delete-by-filter` | irreversible report deletion | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say reports are removed from the dashboard report list and bulk delete can remove multiple reports |
| `community-reviews delete`, `community-reviews bulk-create`, `community-reviews bulk-delete`, `community-reviews remove-reply`, `community-reviews update-moderation-status`, `community-reviews bulk-update-moderation-status` | irreversible review or moderation write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say Reviews is stores-only, delete removes reviews, and bulk or moderation writes can affect public review state |
| `community-review-requests delete`, `community-review-requests bulk-cancel-by-filter` | irreversible review-request write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say only canceled requests can be deleted and bulk cancel starts an async job |
| `community-moderation-rules create`, `community-moderation-rules update`, `community-moderation-rules delete` | irreversible moderation policy write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say moderation rules automate content moderation and each trigger needs a separate rule |
| `inbox-messages send` | irreversible message send | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs say it sends a message to the business or participant and can send notifications |
| `interactive-form-sessions create`, `interactive-form-sessions create-streamed`, `interactive-form-sessions send-message`, `interactive-form-sessions send-message-streamed` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | use the official `dryRun` body field for test sessions where appropriate; streamed commands may return raw event-stream text |
| `intake-forms archive`, `intake-forms unarchive`, `intake-forms update-expiration-period`, `intake-form-submissions extend`, `intake-form-submissions exempt` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | use `--receipt-out` when applying; verification is provider-response based |
| `intake-forms delete`, `intake-form-submissions cancel`, `intake-form-submissions delete` | irreversible write | `--plan-out` for review, then `--plan-in --apply --yes --ack-irreversible` | use `--receipt-out` when applying; official docs warn about deleted/orphaned forms or non-reactivatable canceled submissions |
| `community-groups create`, `community-groups update`, `community-groups delete` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | `delete` also requires `--ack-irreversible`; receipt recommended with `--receipt-out`; verify by provider response plus `community-groups get` or `query` when possible |
| `email-subscriptions upsert`, `email-subscriptions bulk-upsert`, `email-subscriptions generate-unsubscribe-link` | reviewed-plan write | `--plan-out` for review, then `--plan-in --apply --yes` | receipt recommended with `--receipt-out`; verify by provider response plus `email-subscriptions query` when possible |

## When to refuse

- If the target is ambiguous.
- If required config/auth is missing.
- If a write is requested without plan-first review.
- If the requested family is not in this boundary.
- If runtime cannot enforce the safety loop.
