# Engineering notes

This page keeps the short history of real problems we hit and how we solved them.

It is here to reduce repeated debugging, not to tell the whole build story.

Guidelines:
- Keep entries short and factual.
- Link to the provider doc and the PR or issue when that helps.
- Never include secrets.

## 2026-06-29 - Headless Recovery sends an out-of-band reset email

- Symptom: the Headless Recovery row was open after OAuth Apps and Authentication were split into exact Headless subfamilies.
- Root cause: official Wix docs define a single callable Recovery method, Send Recovery Email, and its effect happens through email delivery plus the Wix-managed reset page.
- Fix: shipped explicit `headless-recovery send-recovery-email` on `POST /_api/iam/recovery/v1/send-email`.
- Safety note: the command is reviewed-plan first and requires `--ack-irreversible` because it sends a password-reset email. Plans record the official published-site and allowed-redirect prerequisites, and verification is provider-response-only.
- Validation: focused Headless Recovery command plus docs/wrapper/inventory/formatting suite passed with 214 tests.
- References: Headless Recovery links in `docs/references.md`.

## 2026-06-29 - Headless Redirects has an official endpoint mismatch

- Symptom: the Headless Redirects row was open after Recovery, but the official docs showed different endpoint roots across the rendered method page, generated schema markdown, and REST guide.
- Root cause: Create Redirect Session is the only callable method, and it creates single-use visitor-flow URLs for auth, logout, checkout, product, and booking flows.
- Fix: shipped explicit `headless-redirects create-redirect-session` and used the rendered method page endpoint, `POST /_api/redirects-api/v1/redirect-session`.
- Safety note: the command is reviewed-plan first and requires `--ack-irreversible`; plans record the official published-site and allowed-domain/authorization-redirect prerequisites. `sessionToken` is redacted, while returned redirect URLs stay visible because they are the command result.
- Validation: focused Headless Redirects validation is recorded in `docs/proof.md`.
- References: Headless Redirects links in `docs/references.md`.

## 2026-06-29 - Headless Sitemap has an example endpoint mismatch

- Symptom: the Headless Sitemap row was open after Redirects, and the official rendered page/schema disagreed with the official curl example on the endpoint path.
- Root cause: List Sitemap Pages is the only callable method. It reads sitemap entries by official item type and optional cursor paging.
- Fix: shipped explicit read-only `headless-sitemap list-pages` and used the rendered method page plus embedded schema endpoint, `GET /v1/list-sitemap-pages`.
- Safety note: the command validates the official item-type enum, the official 0-200 paging limit, and non-empty cursor values; no write gates are needed because the method is read-only.
- Validation: focused Headless Sitemap command plus docs/wrapper/inventory/formatting suite passed with 217 tests.
- References: Headless Sitemap links in `docs/references.md`.

## 2026-06-29 - Headless Verification is preview and has an endpoint mismatch

- Symptom: the Headless Verification row was open after Sitemap, and the official rendered page disagreed with the generated markdown schema on the endpoint path.
- Root cause: Verify During Authentication is the only callable method. It submits an email verification code and state token from a `REQUIRE_EMAIL_VERIFICATION` auth flow, and the rendered page marks the method Developer Preview.
- Fix: shipped explicit `headless-verification verify-during-authentication` and used the rendered method page endpoint, `POST /_api/iam/verification/v1/auth/verify`.
- Safety note: the command is reviewed-plan first. Code, state token, session token, access token, and refresh token values are redacted, and token retrieval stays in Headless Authentication.
- Validation: focused Headless Verification validation is recorded in `docs/proof.md`.
- References: Headless Verification links in `docs/references.md`.

## 2026-06-29 - Analytics Sessions is beta and has named async plus state writes

- Symptom: the Analytics Sessions row was still open even though Analytics Data and Semantic Models were already shipped.
- Root cause: official Wix docs define a select-beta Sessions family with one result read, one async list job starter, and two recording-state mutation methods.
- Fix: shipped explicit `analytics-sessions get-list-job-result`, `list-async`, `mark-recordings-deleted`, and `mark-session-recorded` commands.
- Safety note: `list-async` is only a named job starter, not a generic async runner. It requires one session filter and one time period. The two recording-state mutation commands require `--ack-irreversible`.
- Validation: focused Analytics Sessions command tests cover parser exposure, official paths, reviewed-plan writes, acknowledgement gates, and request validation.
- References: Analytics Sessions links in `docs/references.md`.

## 2026-06-29 - AI Site-Chat splits into four explicit families

- Symptom: the broad AI Site-Chat row hid separate Widget Settings, Widget Settings V2, Conversations, and Messages surfaces with different auth and release states.
- Root cause: official Wix docs define AI Site-Chat as three services, while Widget Settings also has deprecated v1 pages and Developer Preview v2 pages.
- Fix: split the row into four official families and exposed only named commands: `ai-site-chat-widget-settings`, `ai-site-chat-widget-settings-v2`, `ai-site-chat-conversations`, and `ai-site-chat-messages`.
- Safety note: settings writes use the reviewed-plan write flow. `ai-site-chat-messages bulk-create` also requires `--ack-irreversible` because it sends chat messages. Visitor-scoped conversation/message methods require site visitor or site member identity.
- Validation: focused AI Site-Chat command tests cover parser exposure, official paths, reviewed-plan writes, and message body validation.
- References: AI Site-Chat links in `docs/references.md`.

## 2026-06-29 - CRM Cards are Developer Preview and include broad tag writes

- Symptom: the CRM Pipelines Management Cards row was still open after Pipelines shipped.
- Root cause: official Wix docs define Cards as a separate Developer Preview family with 10 callable methods and 7 callback-only events.
- Fix: shipped explicit `crm-cards` commands for create, get, update, delete, query, search, bulk tag updates, move, and search by stage.
- Safety note: update requires the current card revision, delete permanently removes the card, move stays within one pipeline, and bulk update tags by filter can affect every card in a pipeline when no filter is supplied.
- Validation: focused CRM Cards command tests passed with 4 tests before docs-wide validation.
- References: CRM Cards links in `docs/references.md`.

## 2026-06-28 - Community Group Rules replacement is all-or-nothing

- Symptom: the open Community row still grouped Group Rules with group requests, member management, and feedback moderation.
- Root cause: official Wix docs define Group Rules as a small callable family under `/social-groups/v2/rules/{groupId}` plus a callback-only Group Rules Updated event.
- Fix: shipped explicit `community-group-rules list` and `create-or-replace` commands. The write uses reviewed plans and requires `--ack-irreversible`.
- Safety note: official docs say Create Or Replace All Rules creates rules if none exist, otherwise replaces all existing rules. The group rules object supports up to 100 rules.
- Validation: focused Community Group Rules command tests passed with 4 tests before docs-wide validation.
- References: Community Group Rules links in `docs/references.md`.

## 2026-06-28 - Community Create Group Requests are decision writes

- Symptom: the remaining Community row still grouped create-group-request decisions with member management and moderation surfaces.
- Root cause: official Wix docs define Create Group Requests as a small callable family under `/_api/social-groups-proxy/group-requests/v2/group-requests` plus approved/rejected callback events.
- Fix: shipped explicit `community-group-requests list`, `query`, `approve`, and `reject` commands. Approve and reject use reviewed plans and require `--ack-irreversible`.
- Safety note: official docs say only Wix users can approve or reject group requests, and both writes trigger callback events.
- Validation: focused Community Group Requests command tests passed with 6 tests before docs-wide validation.
- References: Community Create Group Requests links in `docs/references.md`.

## 2026-06-28 - Community Group Members writes can invite or remove members

- Symptom: the open Community row still grouped group-member membership changes with roles, join requests, membership questions, and moderation surfaces.
- Root cause: official Wix docs define Group Members as a callable Member Management family under `/social-groups-proxy/members/v2`.
- Fix: shipped explicit `community-group-members list`, `list-memberships`, `query`, `query-memberships`, `add`, and `remove` commands. Add and remove use reviewed plans and require `--ack-irreversible`.
- Safety note: official docs say adding public members adds them right away, private members receive an invitation, and removing members triggers Member Removed.
- Validation: focused Community Group Members command tests passed with 8 tests before docs-wide validation.
- References: Community Group Members links in `docs/references.md`.

## 2026-06-28 - Community Group Roles changes group permissions

- Symptom: the open Community row still grouped role changes with join requests, membership questions, and feedback moderation.
- Root cause: official Wix docs define Group Roles as a callable Member Management family under `/social-groups-proxy/roles/v2/groups`.
- Fix: shipped explicit `community-group-roles assign` and `unassign` commands. Both use reviewed plans and require `--ack-irreversible`.
- Safety note: assigning a role overrides the member's current `role.value`; unassign only supports `ADMIN` roles and changes group permissions.
- Validation: focused Community Group Roles command tests passed with 4 tests before docs-wide validation.
- References: Community Group Roles links in `docs/references.md`.

## 2026-06-28 - Community Join Requests decide private group membership

- Symptom: the open Community row still grouped private-group join requests with membership questions and moderation surfaces.
- Root cause: official Wix docs define Join Group Requests as a callable Member Management family under `/social-groups-proxy/join/v2/groups/{groupId}/join-requests`.
- Fix: shipped explicit `community-join-requests list`, `query`, `approve`, and `reject` commands. Approve and reject use reviewed plans and require `--ack-irreversible`.
- Safety note: official docs say this family is only relevant for private groups, and approving a request adds the site member to the group.
- Validation: focused Community Join Requests command tests passed with 6 tests before docs-wide validation.
- References: Community Join Group Requests links in `docs/references.md`.

## 2026-06-29 - Community Membership Questions is a full-set replacement write

- Symptom: the open Community row still grouped membership questions with feedback moderation surfaces.
- Root cause: official Wix docs define Membership Questions as a callable Member Management family under `/social-groups-proxy/questions/v2/membership-questions`.
- Fix: shipped explicit `community-membership-questions list`, `list-answers`, and `create-or-replace` commands. The write uses reviewed plans and requires `--ack-irreversible`.
- Safety note: official docs say create-or-replace creates questions when none exist, otherwise replaces all existing questions; `--questions-json` must be Wix's official object with a `questions` array, and an empty questions array means members will not have to answer any question when joining.
- Validation: focused Community Membership Questions command tests passed with 7 tests before docs-wide validation.
- References: Community Membership Questions links in `docs/references.md`.

## 2026-06-29 - Community Reports V2 deletes are dashboard report removals

- Symptom: the broad Feedback & Moderation row still grouped Reports V2 with Comments, Reviews, Review Requests, and Moderation Rules.
- Root cause: official Wix docs define Reports V2 as a callable Feedback & Moderation family under `/reports/v2/reports`.
- Fix: shipped explicit `community-reports get`, `query`, `count-by-reason-types`, `create`, `update`, `upsert`, `delete`, and `bulk-delete-by-filter` commands. Create, update, and upsert use reviewed plans; delete and bulk-delete-by-filter require `--ack-irreversible`.
- Safety note: official docs say Reports V2 is currently supported for Wix Comments only. They also say delete removes a report from the dashboard report list, and bulk-delete-by-filter deletes multiple reports by filter.
- Validation: focused Community Reports V2 command tests passed with 4 tests before docs-wide validation.
- References: Community Reports V2 links in `docs/references.md`.

## 2026-06-29 - Community Comments moderation writes need stronger approval

- Symptom: the broad Feedback & Moderation row still had Comments open after Reports V2 shipped.
- Root cause: official Wix docs define Comments as a callable Feedback & Moderation family under `/comments/v1/comments` and `/comments/v1/bulk/comments`.
- Fix: shipped explicit `community-comments` commands for create, get, update, delete, moderate-draft-content, query, mark, unmark, hide, publish, count, list-by-resource, get-thread, bulk-publish, bulk-hide, bulk-delete, bulk-moderate-draft-content, and bulk-move-by-filter.
- Safety note: create and update are reviewed-plan writes. Delete, moderation-state writes, and all bulk writes require `--ack-irreversible` because official docs say delete removes comment content, publish/hide/mark/unmark/moderation change comment state, and bulk methods can affect multiple comments.
- Validation: focused Community Comments command tests passed with 4 tests before docs-wide validation.
- References: Community Comments links in `docs/references.md`.

## 2026-06-29 - Community Reviews is stores-only and has moderation writes

- Symptom: after Comments shipped, the next Feedback & Moderation row was Reviews.
- Root cause: official Wix docs define Reviews as a callable family under `/reviews/v1/reviews` and `/reviews/v1/bulk/reviews`, and say Reviews is currently only available with the `stores` namespace.
- Fix: shipped explicit `community-reviews` commands for get, query, count, create, update, delete, bulk-create, bulk-delete, remove-reply, set-reply, update-moderation-status, and bulk-update-moderation-status.
- Safety note: create, update, and set-reply are reviewed-plan writes. Delete, remove-reply, moderation-status changes, and bulk actions require `--ack-irreversible` because they delete review content or replies, change moderation/publication state, or affect multiple reviews.
- Validation: focused Community Reviews command tests passed with 4 tests before docs-wide validation.
- References: Community Reviews links in `docs/references.md`.

## 2026-06-29 - Review Request bulk cancel starts an async job

- Symptom: after Reviews shipped, the next Feedback & Moderation row was Review Requests.
- Root cause: official Wix docs define Review Requests as a callable family under `/reviews/v2/review-requests` and `/reviews/v2/bulk/review-requests`, and say Review Requests is currently only available with the `stores` namespace.
- Fix: shipped explicit `community-review-requests` commands for create, get, delete, query, count, and bulk-cancel-by-filter.
- Safety note: create is a reviewed-plan write. Delete and bulk-cancel-by-filter require `--ack-irreversible`; official docs say only canceled review requests can be deleted, and bulk cancel starts a bulk async job. The CLI exposes the named cancel method but does not add a generic async-job runner.
- Validation: focused Community Review Requests command tests passed with 4 tests before docs-wide validation.
- References: Community Review Requests links in `docs/references.md`.

## 2026-06-29 - Moderation Rules change automatic content policy

- Symptom: after Review Requests shipped, the next Feedback & Moderation row was Moderation Rules.
- Root cause: official Wix docs define Moderation Rules as a callable family under `/moderation/v1/rules`; rules automate moderation for newly submitted comments and reviews.
- Fix: shipped explicit `community-moderation-rules` commands for create, get, update, delete, query, and check-content.
- Safety note: create, update, and delete require `--ack-irreversible` because rules can automatically approve, reject, or send future content for manual approval. `check-content` is a non-mutating helper.
- Validation: focused Community Moderation Rules command tests passed with 4 tests before docs-wide validation.
- References: Community Moderation Rules links in `docs/references.md`.

## 2026-06-29 - Inbox Channels has no separate callable method page

- Symptom: the Communication row grouped Inbox and Channels after the Community Feedback and Moderation rows were shipped.
- Root cause: the current official Inbox menu exposes Conversations and Messages method pages. It does not expose a separate callable Channels method page.
- Fix: split the row into Inbox Conversations, Inbox Messages, and a docs-only Inbox Channels note. Shipped explicit `inbox-conversations get|get-or-create` and `inbox-messages list|send` commands.
- Safety note: `inbox-conversations get-or-create` is a reviewed-plan write because it may create a conversation. `inbox-messages send` requires `--ack-irreversible` because official docs say it sends a message to the business or participant and can send notifications.
- Validation: focused Inbox command tests passed with 4 tests before docs-wide validation.
- References: Inbox links in `docs/references.md`.

## 2026-06-29 - Loyalty Program Program is a site-wide settings slice

- Symptom: after Inbox shipped, the next open CRM row was the broad Loyalty Program area.
- Root cause: official Wix docs split Loyalty Program into Program, Earning Rules, Tiers, Accounts, Rewards, and CRM areas. Program has seven callable methods and one callback-only event.
- Fix: shipped explicit `loyalty-program get|premium-features|update|activate|pause|enable-points-expiration|disable-points-expiration` commands for the Program slice only. The remaining Loyalty areas stay open in `docs/api_coverage.md`.
- Safety note: `update`, `activate`, `pause`, `enable-points-expiration`, and `disable-points-expiration` require `--ack-irreversible` because they change program-wide loyalty settings, status, or points-expiration behavior.
- Validation: focused Loyalty Program command tests passed with 4 tests before docs-wide validation.
- References: Loyalty Program links in `docs/references.md`.

## 2026-06-29 - Loyalty Earning Rules change point earning behavior

- Symptom: after the Program slice shipped, the next Loyalty row was Earning Rules.
- Root cause: official Wix docs define Earning Rules as a separate callable family for listing, reading, creating, updating, deleting, bulk creating, creating custom automated rules, and deleting custom automated rules.
- Fix: shipped explicit `loyalty-earning-rules list|get|create|update|delete|bulk-create|create-custom|delete-automation` commands.
- Safety note: all Earning Rules writes require `--ack-irreversible` because they change how customers earn loyalty points. `update` requires `earningRule.revision`, and `delete` requires the current `revision` query value.
- Endpoint note: official method endpoint headers and fetch examples include the `/_api/loyalty-earning-rules` root, while some curl examples omit `/_api`; the CLI follows the endpoint headers and fetch examples.
- Validation: focused Loyalty Earning Rules command tests passed with 4 tests before docs-wide validation.
- References: Loyalty Program links in `docs/references.md`.

## 2026-06-29 - Loyalty Tiers change benefit thresholds

- Symptom: after Earning Rules shipped, the next Loyalty row was Tiers.
- Root cause: official Wix docs define Tiers as a separate callable family for tier reads, tier lifecycle writes, bulk create, get-program, and global tiers program settings.
- Fix: shipped explicit `loyalty-tiers list|get|create|update|delete|bulk-create|get-program|create-program-settings|get-program-settings|update-program-settings` commands.
- Safety note: Tiers writes require `--ack-irreversible` because they change tier definitions, point thresholds, or global tier program settings. `get-program` is guarded because official docs say it creates default program settings if none exist, `delete` requires the current `revision` query value, and `update-program-settings` requires `programSettings.status`, `revision`, and `rollingWindow`.
- Validation: focused Loyalty Tiers command tests passed with 4 tests before docs-wide validation.
- References: Loyalty Program links in `docs/references.md`.

## 2026-06-29 - Loyalty Accounts writes change customer point balances

- Symptom: after Tiers shipped, the next Loyalty row was Accounts.
- Root cause: official Wix docs define Loyalty Accounts as a callable family for deprecated list compatibility, account get/query/search/count, program totals, current-member and secondary-ID account lookup, account creation, point adjustment, bulk point adjustment, and manually earning points.
- Fix: shipped explicit `loyalty-accounts list|get|query|search|count|get-program-totals|get-current-member-account|get-by-secondary-id|create|adjust-points|bulk-adjust-points|earn-points` commands.
- Safety note: account creation and all point-balance writes require `--ack-irreversible`. `adjust-points` requires the current `revision`; `bulk-adjust-points` requires a `search` selector and returns an async job ID, but the CLI does not add a generic async-job runner.
- Validation: focused Loyalty Accounts command tests cover all callable Accounts methods before docs-wide validation.
- References: Loyalty Program links in `docs/references.md`.

## 2026-06-29 - Loyalty Rewards writes change redeemable reward definitions

- Symptom: after Accounts shipped, the next Loyalty row grouped Rewards, Checkout Discount, and Coupons.
- Root cause: official Wix docs define a separate Rewards subfamily for reward definition reads and lifecycle writes. Checkout Discount and Coupons are separate official subfamilies tracked in their own rows.
- Fix: shipped explicit `loyalty-rewards list|get|query|create|bulk-create|update|delete` commands.
- Safety note: reward create, bulk create, update, and delete require `--ack-irreversible` because they change what customers can redeem with loyalty points. The CLI keeps events callback-only and does not use a generic Rewards bridge for Checkout Discount or Coupons.
- Validation: focused Loyalty Rewards command tests cover parser exposure, official paths, write dry-runs, and body validation before docs-wide validation.
- References: Loyalty Rewards links in `docs/references.md`.

## 2026-06-29 - Loyalty Checkout Discount can redeem checkout rewards

- Symptom: the split Checkout Discount row was still open after reward definitions shipped.
- Root cause: official Wix docs define Checkout Discount as a separate Rewards subfamily with query and apply methods for eCommerce checkouts.
- Fix: shipped explicit `loyalty-checkout-discounts query|apply` commands.
- Safety note: apply requires a reviewed plan plus `--ack-irreversible` because it can redeem points or apply a loyalty/referral reward to an eCommerce checkout.
- Validation: focused Loyalty Checkout Discounts command tests cover parser exposure, official paths, query defaults, write dry-runs, and body validation.
- References: Loyalty Checkout Discount links in `docs/references.md`.

## 2026-06-29 - Loyalty Coupons redeem points and create reference coupons

- Symptom: after Checkout Discount shipped, the split Loyalty Coupons row was still open.
- Root cause: official Wix docs define Loyalty Coupons as a separate Rewards subfamily with read/query/current-member methods plus redeem and delete methods under `/loyalty-coupons/v1/coupons`.
- Fix: shipped explicit `loyalty-coupons get|query|get-current-member|redeem-current-member|redeem|delete` commands.
- Safety note: redeem and delete require reviewed plans plus `--ack-irreversible` because redeeming creates loyalty coupons from customer points and delete removes the loyalty coupon record. Official docs say deleting the loyalty coupon does not affect the corresponding reference coupon.
- Validation: focused Loyalty Coupons command tests cover parser exposure, official paths, write dry-runs, and body validation.
- References: Loyalty Coupons links in `docs/references.md`.

## 2026-06-29 - Loyalty Transactions are read-only account activity records

- Symptom: after the Rewards subfamilies shipped, the next broad Loyalty Program CRM row hid exact remaining account work.
- Root cause: official Wix docs do not expose a separate `/loyalty-program/crm` API page. The remaining Loyalty Accounts area splits into Transactions, Social Media, and Imports.
- Fix: split the broad row and shipped explicit `loyalty-transactions get|query` commands for the official Transactions subfamily.
- Safety note: Transactions commands are read-only. They do not change points or account state.
- Validation: focused Loyalty Transactions command tests cover parser exposure, official paths, and required transaction ID validation.
- References: Loyalty Transactions links in `docs/references.md`.

## 2026-06-29 - Loyalty Social Media needs member-context writes

- Symptom: after Transactions shipped, the next split Loyalty Accounts subfamily was Social Media.
- Root cause: official Wix docs define Social Media as a separate Accounts subfamily for followed-channel records, with one read method, one write method, and one event.
- Fix: shipped explicit `loyalty-social-media list|create` commands.
- Safety note: create requires reviewed plans plus `--ack-irreversible` because following a channel can award loyalty points. Official docs say both methods require visitor or member authentication, and members can only follow channels enabled in the dashboard.
- Validation: focused Loyalty Social Media command tests cover parser exposure, official paths, write dry-runs, and body validation.
- References: Loyalty Social Media links in `docs/references.md`.

## 2026-06-29 - Loyalty Imports can overwrite point balances

- Symptom: after Social Media shipped, the next split Loyalty Accounts subfamily was Imports.
- Root cause: official Wix docs define Imports as a separate Accounts subfamily under `/_api/loyalty-imports/v1/loyalty-imports`.
- Fix: shipped explicit `loyalty-imports get|query|create-file-url|create|execute|get-error-file-download-url` commands.
- Safety note: `create-file-url` is a reviewed-plan helper write. `create` and `execute` require `--ack-irreversible` because importing CSV point balances can overwrite existing customer point balances.
- Validation: focused Loyalty Imports command tests cover parser exposure, official paths, write dry-runs, and body validation.
- References: Loyalty Imports links in `docs/references.md`.

## 2026-06-29 - CRM core split into Tasks and Pipelines

- Symptom: the next open CRM row was too broad to implement as one honest command family.
- Root cause: official Wix docs split CRM into Tasks and Pipelines Management, and Pipelines Management has separate Pipelines and Cards surfaces.
- Fix: split the broad row, shipped explicit `crm-tasks create|get|update|delete|query|count|move-after` commands, and left Pipelines and Cards as exact open rows.
- Safety note: `create`, `update`, and `move-after` are reviewed-plan writes. `delete` requires `--ack-irreversible` because it removes a CRM task. `update` validates `task.revision` before planning.
- Validation: focused CRM Tasks command tests cover parser exposure, official paths, write dry-runs, ack gating, and body validation.
- References: CRM Tasks links in `docs/references.md`.

## 2026-06-29 - CRM Pipelines are Developer Preview and can affect all pipelines by filter

- Symptom: after CRM Tasks shipped, the next exact CRM row was Pipelines Management - Pipelines.
- Root cause: official Wix docs define seven callable Pipelines methods under `/crm/pipelines/v1` plus three webhook events, and all callable method pages are marked Developer Preview.
- Fix: shipped explicit `crm-pipelines create|get|update|delete|query|bulk-update-tags|bulk-update-tags-by-filter` commands and kept Cards as the next exact open row.
- Safety note: `delete` requires `--ack-irreversible` because deleting a pipeline permanently removes it. `bulk-update-tags-by-filter` also requires `--ack-irreversible` because omitting a filter updates every pipeline and the method returns an async job ID.
- Validation: focused CRM Pipelines command tests cover parser exposure, official paths, write dry-runs, ack gating, and body validation.
- References: CRM Pipelines links in `docs/references.md`.

## 2026-06-28 - Intake Form Submissions has mixed endpoint roots

- Symptom: after Interactive Form Sessions shipped, the next Forms row still had Intake Forms and Intake Form Submissions open.
- Root cause: official Wix docs define two callable Other Services families. Intake Forms uses `/_api/intake-forms/v1/intake-forms...`; most Intake Form Submissions methods use `/_api/intake-forms/v1/submissions...`, but Count Submissions By Intake Form Ids uses `/_api/intake-forms/v1/submissions/count`.
- Fix: shipped explicit `intake-forms` and `intake-form-submissions` commands and preserved the official count-path exception instead of inventing one normalized base path.
- Safety note: form delete requires `--ack-irreversible` because Wix deletes the underlying form and hides orphaned submissions from this API. Submission cancel and delete also require `--ack-irreversible`; official docs say canceled submissions cannot be reactivated.
- Validation: focused Intake Forms command tests passed with 6 tests before docs-wide validation.
- References: Forms Intake Forms and Forms Intake Form Submissions links in `docs/references.md`.

## 2026-06-28 - Interactive Form Sessions are Developer Preview and can stream events

- Symptom: the open Forms row still grouped Interactive Form Sessions with service plugin and intake-form areas.
- Root cause: official Wix docs define Interactive Form Sessions as a separate Developer Preview callable family under `/forms/ai/v1/interactive-form-sessions`; the streamed methods return `text/event-stream`, and the Forms menu endpoint did not list every method page even though official raw method pages exist.
- Fix: shipped explicit `interactive-form-sessions` commands for create, create streamed, send user message, send user message streamed, and generate form summary. Create and send-message commands are reviewed-plan writes; the summary method is a non-mutating helper.
- Safety note: plans preserve the official `dryRun` body field, streamed applies return JSON when possible or raw event-stream text, and `send-message` validates the official 10,000-character input limit.
- Validation: focused Interactive Form Sessions command tests passed with 5 tests before docs-wide validation.
- References: Forms Interactive Form Sessions links in `docs/references.md`.

## 2026-06-28 - Chat Settings changes affect future interactive form sessions

- Symptom: the open Forms row still grouped Chat Settings with Interactive Form Sessions and service plugins.
- Root cause: official Wix docs define Chat Settings as a separate callable family under `/forms/ai/v1/chat-settings`, while events remain callback-only.
- Fix: shipped explicit `chat-settings` commands for get, query, create, update, and delete. Create and update are reviewed-plan writes; update requires the current `chatSettings.revision`; delete requires `--ack-irreversible` because it removes the AI chat settings entity for a form.
- Validation: focused Chat Settings command tests passed with 4 tests before docs-wide validation.
- References: Forms Chat Settings links in `docs/references.md`.

## 2026-06-28 - Community Groups has group visibility side effects

- Symptom: the open Community row grouped Groups with rules, requests, member management, and feedback moderation.
- Root cause: official Wix docs define Community Groups core as a separate callable family under `/social-groups-proxy/groups/v2/groups`, while group events remain callback-only.
- Fix: shipped explicit `community-groups` commands for list, get, get by slug, query, create, update, and delete. Create and update are reviewed-plan writes; delete requires `--ack-irreversible`.
- Safety note: official docs say only group admins can update groups, private-to-public updates approve pending join requests, private-to-secret updates reject pending join requests, and group-name updates can change the slug.
- Validation: focused Community Groups command tests passed with 4 tests before docs-wide validation.
- References: Community Groups links in `docs/references.md`.

## 2026-06-28 - Email Subscriptions is Developer Preview and changes marketing state

- Symptom: the open Communication row grouped Email Subscriptions with Inbox and Channels.
- Root cause: official Wix docs define Email Subscriptions as a separate Developer Preview callable family under `/email-marketing/v1/email-subscriptions`, while Email Subscription Changed remains callback-only.
- Fix: shipped explicit `email-subscriptions` commands for query, upsert, bulk upsert, and unsubscribe-link generation. Query is a read/helper; the other three commands are reviewed-plan writes.
- Safety note: official docs say unsubscribe-link generation only changes a recipient to `UNSUBSCRIBED` if the recipient uses the link, but the command still creates a provider-side unsubscribe URL and therefore stays plan-first.
- Validation: focused Email Subscriptions command tests passed with 4 tests before docs-wide validation.
- References: Communication Email Subscriptions links in `docs/references.md`.

## 2026-06-28 - Form Schemas deletes have trash and permanent-removal paths

- Symptom: the open Forms row still grouped Form Schemas with chat settings, interactive sessions, and service plugins.
- Root cause: official Wix docs define Form Schemas as a separate callable family under `/form-schema-service/v4`.
- Fix: shipped explicit `form-schemas` commands for active/deleted form reads, query/count helpers, provider config reads, summaries, create/update/clone/bulk writes, trash restore/removal, and deleted-field removal. Trash, permanent delete, bulk delete, and deleted-field removal require `--ack-irreversible`.
- Validation: focused Form Schemas command tests passed with 4 tests before docs-wide validation.
- References: Form Schemas links in `docs/references.md`.

## 2026-06-28 - Contacts V4 bulk jobs need stronger review

- Symptom: the broad Members & Contacts remaining row still hid Contacts V4 writes, facets, merge, and bulk job coverage.
- Root cause: official Wix docs define Contacts V4 callable methods beyond the read-only `list`, `get`, and `query` subset that was already shipped.
- Fix: expanded `contacts` with explicit named commands for facets, bulk-job read, merge preview, single-contact writes, label/unlabel, and bulk jobs. Delete, merge, and bulk jobs require `--ack-irreversible`; update requires `contact.revision`.
- Validation: focused Contacts command tests passed with 7 tests before docs-wide validation.
- References: Contacts V4 links in `docs/references.md`.

## 2026-06-28 - Contact Attachments upload URLs are write-like

- Symptom: the broad Members & Contacts remaining row still hid contact file attachment work after contact notes were shipped.
- Root cause: official Wix docs define Contact Attachments V4 as a separate callable family under `/contacts/v4/attachments`.
- Fix: shipped explicit `contact-attachments get`, `list`, `generate-upload-url`, and `delete` commands, kept upload URL generation and delete behind reviewed-plan write flow, and required `--ack-irreversible` for delete because it removes a saved contact file attachment.
- Validation: focused Contact Attachments command tests passed with 3 tests before docs-wide validation.
- References: Contact Attachments links in `docs/references.md`.

## 2026-06-28 - Contact Notes updates require current revisions

- Symptom: the broad Members & Contacts remaining row still hid contact note work after contact labels and extended fields were shipped.
- Root cause: official Wix docs define Contact Notes V2 as a separate callable family under `/crm/notes/v2/notes`.
- Fix: shipped explicit `contact-notes get`, `query`, `create`, `update`, and `delete` commands, kept writes reviewed-plan first, and required `--ack-irreversible` for delete because it removes a saved contact note.
- Validation: focused Contact Notes command tests passed with 3 tests before docs-wide validation.
- References: Contact Notes links in `docs/references.md`.

## 2026-06-28 - Contact Extended Fields delete removes stored contact values

- Symptom: the broad Members & Contacts remaining row still hid contact field-definition work after contact labels were already shipped.
- Root cause: official Wix docs define Contact Extended Fields as a separate callable family under `/contacts/v4/extended-fields`.
- Fix: shipped explicit `contact-extended-fields get`, `list`, `query`, `find-or-create`, `update`, and `delete` commands, kept writes reviewed-plan first, and required `--ack-irreversible` for delete because Wix says stored contact values for that field are permanently deleted.
- Validation: focused Contact Extended Fields command tests passed with 3 tests before docs-wide validation.
- References: Contact Extended Fields links in `docs/references.md`.

## 2026-06-28 - Member Authentication sends a one-time password email

- Symptom: after Custom Field Suggestions shipped, the broad Members remaining row still included Member Authentication.
- Root cause: official Wix docs define one Developer Preview callable method for sending a set-password email under `/wix-sm/api/v1/auth/v1/auth/members/send-set-password-email`.
- Fix: shipped explicit `member-authentication send-set-password-email`, kept it reviewed-plan first, and required `--ack-irreversible` because the email side effect cannot be unsent.
- Validation: focused Member Authentication command tests passed with 2 tests before docs-wide validation.
- References: Members Member Authentication links in `docs/references.md`.

## 2026-06-28 - Members Custom Field Suggestions is read-only

- Symptom: after Custom Field Applications shipped, the remaining Members row still included the suggested-profile-fields API.
- Root cause: official Wix docs define Custom Field Suggestions as a separate read family under `/members/v1/custom-field-suggestions`.
- Fix: shipped explicit `member-custom-field-suggestions query` and `list` commands, kept both read-only, and recorded the official Developer Preview marker for `list`.
- Validation: focused Members Custom Field Suggestions/docs/wrapper/inventory/formatting suite passed with 145 tests.
- References: Members Custom Field Suggestions links in `docs/references.md`.

## 2026-06-28 - Members Custom Field Applications delete expands field access

- Symptom: after Custom Fields shipped, the remaining Members row still included the audience-rules API for those fields.
- Root cause: official Wix docs define Custom Field Applications as a separate callable family under `/members/v1/custom-fields-applications`.
- Fix: shipped explicit `member-custom-field-applications create`, `update`, `delete`, `get`, `list-applications`, `get-members`, and `get-roles` commands, kept writes reviewed-plan first, and required `--ack-irreversible` for delete because Wix says deleting an application makes the field apply to all members.
- Validation: focused Members Custom Field Applications/docs/wrapper/inventory/formatting suite passed with 145 tests.
- References: Members Custom Field Applications links in `docs/references.md`.

## 2026-06-28 - Members Custom Fields shipped as its own Members family

- Symptom: the broad Members remaining row still included Custom Fields after the Privacy slice.
- Root cause: official Wix docs define Custom Fields as a separate callable family under `/members/v1/custom-fields`.
- Fix: shipped explicit `member-custom-fields create`, `update`, `delete`, `get`, `hide`, `list`, and `update-order` commands, kept writes reviewed-plan first, and required `--ack-irreversible` for delete.
- Validation: focused Members Custom Fields/docs/wrapper/inventory/formatting suite passed with 144 tests.
- References: Members Custom Fields links in `docs/references.md`.

## 2026-06-28 - Members Activity starts with Activity Counters

- Symptom: the Members Activity row was broad and mixed current families with deprecated badge pages.
- Root cause: official Members Activity contains Activity Counters, legacy Badges, Badges V4, Badge Assignments, Member Reports, and Members Followers. The legacy Badges API is deprecated and replaced by Badges V4 and Badge Assignments.
- Fix: split the broad Activity row, shipped explicit `activity-counters get`, `query`, and `set` commands, kept `set` reviewed-plan first, recorded Activity Counter Updated as callback-only, and classified legacy Badges v3 as deprecated/non-callable.
- Validation: focused Activity Counters command tests passed with 4 tests, and the Activity Counters plus legacy Badges classification docs/inventory suite passed with 137 tests.
- References: Members Activity Counters links in `docs/references.md`.

## 2026-06-28 - Badges V4 delete affects assignments

- Symptom: the current Badges V4 family replaced legacy badge definitions, but badge delete is wider than one badge-definition record.
- Root cause: official Badges V4 docs say deleting a badge removes it from all members who currently have it assigned, while badge assignment itself belongs to the separate Badge Assignments API.
- Fix: shipped explicit `badges-v4 get`, `query`, `create`, `update`, `delete`, and `move` commands, kept writes reviewed-plan first, required `--ack-irreversible` for delete, recorded the deprecated display-order method as non-callable, and recorded badge events as callback-only.
- Validation: focused Badges V4 command tests plus docs/wrapper/inventory contract tests.
- References: Members Activity Badges V4 links in `docs/references.md`.

## 2026-06-28 - Badge Assignments writes can change member access

- Symptom: badge definitions were shipped, but assigning those badges to members was still open.
- Root cause: official Badge Assignments is its own family. Creating assignments can grant badge-linked permissions, while deleting assignments removes those permissions or privileges and cannot be undone.
- Fix: shipped explicit `badge-assignments query`, `create`, `delete`, `bulk-create`, `bulk-delete`, `bulk-update-tags`, and `bulk-update-tags-by-filter` commands, kept writes reviewed-plan first, required `--ack-irreversible` for deletes and broad filter tag updates, and recorded assignment events as callback-only.
- Validation: focused Badge Assignments command tests plus docs/wrapper/inventory contract tests.
- References: Members Activity Badge Assignments links in `docs/references.md`.

## 2026-06-28 - Member Reports are moderation records

- Symptom: Members Activity still had the moderation report family open after badge assignment coverage.
- Root cause: official Member Reports is a separate family for reporting inappropriate member behavior, querying reports, and deleting all reports for one member.
- Fix: shipped explicit `member-reports query`, `report`, and `delete` commands, kept report/delete reviewed-plan first, required `--ack-irreversible` for deleting all reports for a member, and recorded report events as callback-only.
- Validation: focused Member Reports command tests plus docs/wrapper/inventory contract tests.
- References: Members Activity Member Reports links in `docs/references.md`.

## 2026-06-28 - Members Followers changes current-member relationships

- Symptom: Members Activity still had member follow relationships open after moderation report coverage.
- Root cause: official Members Followers is a separate family where the caller follows or unfollows other members, lists follower/following relationships, and checks connection status.
- Fix: shipped explicit `members-followers follow`, `unfollow`, `list-followers`, `list-following`, `list-my-followers`, `list-my-following`, `query-connections`, and `query-my-connections` commands, kept follow/unfollow reviewed-plan first, required `--ack-irreversible` for unfollow, and recorded follow events as callback-only.
- Validation: focused Members Followers command tests plus docs/wrapper/inventory contract tests.
- References: Members Activity Members Followers links in `docs/references.md`.

## 2026-06-28 - User Member is a read-only member/user cross-site query

- Symptom: the broad Members remaining row still mixed User Member with other member-related subfamilies.
- Root cause: official User Member has one callable query method for members that are also Wix users; it is separate from ordinary Members Member Management.
- Fix: shipped explicit `user-members query`, kept it read-only, recorded the official auth and Members Area install requirement, and left the other remaining member subfamilies open.
- Validation: focused User Member command tests plus docs/wrapper/inventory contract tests.
- References: Members User Member links in `docs/references.md`.

## 2026-06-28 - Members About V2 owns rich profile About content

- Symptom: the broad Members remaining row still mixed profile About content with unrelated member areas.
- Root cause: official Members About V2 is a separate family for rich-content About sections on member profiles.
- Fix: shipped explicit `member-abouts create`, `get`, `update`, `delete`, `query`, and `get-my` commands, kept writes reviewed-plan first, required `memberAbout.revision` for update, required `--ack-irreversible` for delete, and recorded About events as callback-only.
- Validation: focused Members About command tests plus docs/wrapper/inventory contract tests.
- References: Members About V2 links in `docs/references.md`.

## 2026-06-28 - Member Privacy has default and current-member override layers

- Symptom: the broad Members remaining row still mixed privacy settings with unrelated member areas.
- Root cause: official Privacy has two subfamilies: Default Privacy for new members and Member Privacy Settings for current-member overrides.
- Fix: shipped explicit `member-privacy get-default`, `set-default`, `get-settings`, and `set-settings` commands, kept writes reviewed-plan first, marked Set Default Privacy Status as Developer Preview, and required `memberPrivacySettings.revision` for settings updates.
- Validation: focused Member Privacy command tests plus docs/wrapper/inventory contract tests.
- References: Members Privacy links in `docs/references.md`.

## 2026-06-29 - Headless Authentication needs command-level redaction

- Symptom: the Headless Authentication row was open, but the official methods return or accept passwords, codes, cookies, session tokens, access tokens, and refresh tokens.
- Root cause: Login V2, Register V2, Retrieve Tokens, Change Password, Logout, and Sign On are distinct official methods with different safety profiles; exposing them without command-level redaction could leak secrets through stdout, plans, receipts, or audit logs.
- Fix: shipped explicit `headless-authentication login-v2`, `retrieve-tokens`, `register-v2`, `change-password`, `logout`, and `sign-on` commands. Login and token retrieval run as sensitive helpers with redacted outputs. Register, password change, logout, and sign-on are reviewed-plan commands; password change and sign-on require `--ack-irreversible`.
- Validation: focused Headless Authentication command plus docs/wrapper/inventory/formatting suite passed with 216 tests; full Wix suite passed with 1654 tests.
- References: Headless Authentication links in `docs/references.md`.

## 2026-06-25 - Calendar Schedules V3 is the current schedule family

- Symptom: Bookings-related calendar coverage was still open after Waitlist and service-plugin boundaries were accounted.
- Root cause: Wix's old Bookings Calendar V1 schedules/sessions docs are legacy and point to the newer Calendar API, while Calendar Schedules V3 is a normal callable schedule family and schedule events are callback-only.
- Fix: shipped explicit `calendar-schedules-v3` get/query/create/update/cancel commands, kept writes reviewed-plan first, required `--ack-irreversible` for cancel, required current `schedule.revision` on update, and documented the Wix Bookings app ID required for schedules to appear in the Bookings calendar.
- Validation: focused Calendar Schedules V3 command tests passed with 6 tests before docs-wide validation.
- References: Calendar Schedules V3 links in `docs/references.md`.

## 2026-06-29 - Automations row split into Storage Items and Automations V2

- Symptom: `docs/api_coverage.md` still had one broad not-yet-implemented Automations row even though official Wix docs expose two distinct callable families.
- Root cause: Automations Storage Items and Automations V2 have separate endpoints, safety risks, callback-only events, and command shapes; keeping them in one row hid real callable coverage work.
- Fix: shipped explicit `automation-storage-items` and `automations-v2` commands, kept trigger/action service plugins callback-only, required `--ack-irreversible` for filtered storage tag updates and automation create/update/delete, and documented the `Set Up Automations` permission.
- Validation: focused Automations command tests and docs/wrapper/inventory contract tests were added for this slice.
- References: Automations Storage Items and Automations V2 links in `docs/references.md`.

## 2026-06-25 - External Calendar V2 replaced legacy Bookings Calendar V1 sync work

- Symptom: Bookings calendar coverage still had an external-calendar gap after Schedules V3 shipped.
- Root cause: legacy Bookings Calendar V1 is compatibility-only, while the current External Calendar V2 docs expose nine callable REST methods for providers, connections, calendars, events, sync configuration, and disconnect.
- Fix: shipped explicit `bookings-external-calendars-v2` commands, kept connect and sync changes reviewed-plan first, required `--ack-external-credentials` for password-based connections, redacted secret fields from plans and receipts, and required `--ack-irreversible` for disconnect because Wix says it deletes Wix calendar events from the external calendar.
- Validation: focused External Calendar V2 command tests passed with 6 tests before docs-wide validation.
- References: Bookings External Calendar V2 links in `docs/references.md`.

## 2026-06-25 - Service Options and Variants is separate from Services V2

- Symptom: the course and service setup flow still pointed to service variant work that was not covered by the existing `bookings-services-v2` command family.
- Root cause: Wix documents Service Options and Variants as its own Bookings services family under `/bookings/v1/serviceOptionsAndVariants`, with separate lifecycle methods and callback events.
- Fix: shipped explicit `bookings-service-options-v1` get/get-by-service-id/query/create/update/delete/clone commands, kept writes reviewed-plan first, required current `serviceOptionsAndVariants.revision` on update, and required `--ack-irreversible` for delete because deleting service options removes varied pricing from the service.
- Validation: focused Service Options and Variants command tests passed with 6 tests before docs-wide validation.
- References: Bookings Service Options and Variants links in `docs/references.md`.

## 2026-06-25 - Bookings Writer V2 mixes public path styles and token auth

- Symptom: the official Writer V2 menu exposes a large method family across normal booking writes, multi-service bookings, allowed-action helpers, and anonymous booking actions.
- Root cause: method pages use a mix of `/_api/bookings-service/...`, `/bookings/...`, `/bookings/multiServiceBookings/...`, and `/v1/anonymous-bookings/...` endpoint shapes, while anonymous action methods use the token itself as the credential.
- Fix: shipped one explicit `bookings-writer-v2` family with each command mapped to its documented endpoint, kept writes reviewed-plan first, required `--ack-irreversible` for higher-risk lifecycle and anonymous mutation commands, capped bulk create at the official `12` bookings, and kept anonymous tokens out of the normal auth path.
- Validation: focused Writer V2/docs/wrapper/inventory suite passed with 71 tests.
- References: Bookings Writer V2 links in `docs/references.md`.

## 2026-06-25 - Time Slots V2 expanded without course, policy, waitlist, attendance, or calendar families

- Symptom: Bookings still had official read-only availability gaps for class event slots and multi-service appointment slots after the first appointment-only Time Slots V2 commands.
- Root cause: the official Time Slots V2 family has separate endpoint paths for appointment availability, event/class time slots, and multi-service appointment availability.
- Fix: shipped explicit read-only commands for `list-event`, `get-event`, `list-multi-service`, and `get-multi-service`, kept `get-event` marked Developer Preview, and kept full course-flow, policy, waitlist, attendance, and calendar-family coverage outside these commands.
- Validation: focused Time Slots V2/docs/wrapper/inventory/docs-wrapper suite passed with 88 tests; the full local suite passed with 874 tests.
- References: Bookings Time Slots V2 links in `docs/references.md`.

## 2026-06-25 - Staff Members stays separate from Resources V2

- Symptom: the remaining Bookings backlog still included staff after Resources V2 and Resource Types V2 shipped.
- Root cause: official Wix docs say Wix automatically manages staff resources and staff resource types, while the Staff Members API owns staff records, schedules, user connections, tags, and trash-bin operations.
- Fix: shipped explicit `bookings-staff-members` commands, kept writes reviewed-plan first, required `--ack-irreversible` for delete and permanent trash-bin removal, required current `staffMember.revision` for update, and capped bulk tag updates by IDs at `100`.
- Validation: focused Staff Members/docs/wrapper/inventory/formatting suite passed with 96 tests.
- References: Bookings Staff Members links in `docs/references.md`.

## 2026-06-25 - Bookings Services V2 writes use provider-response proof

- Symptom: Services V2 has useful service-management writes, but not every write has a cheap before-state snapshot that proves the exact old service state.
- Root cause: official service writes include create, clone, bulk, location replacement, pricing-plan links, slug, and add-on-group methods with mixed response shapes.
- Fix: shipped explicit named commands only, kept writes reviewed-plan first, required `--ack-irreversible` for destructive or replace-style operations, and made receipts say provider-response proof rather than promising automatic rollback.
- Validation: focused Services V2 command tests and docs/wrapper/inventory contract tests.
- References: Bookings Services V2 links in `docs/references.md`.

## 2026-06-25 - Bookings Resources V2 keeps staff resources separate

- Symptom: the Bookings backlog still listed resources as open after services and time-slot reads shipped.
- Root cause: official Resources V2 is its own manageable family for rooms, equipment, and assets, while staff resources are automatically managed by Wix and resource types are a separate API family.
- Fix: shipped explicit Resources V2 commands, kept Resource Types V2 out of this slice, required revisions on update, capped bulk resource requests at `50`, and required `--ack-irreversible` for delete and bulk delete because Wix cancels schedules during deletion.
- Validation: focused Resources V2 command tests and docs/wrapper/inventory contract tests.
- References: Bookings Resources V2 links in `docs/references.md`.

## 2026-06-25 - Bookings Resource Types V2 delete is wider than one record

- Symptom: after Resources V2 shipped, resource classifications were still open and needed their own command family.
- Root cause: official Resource Types V2 is separate from Resources V2, and deleting a resource type also deletes all resources connected to it.
- Fix: shipped explicit Resource Types V2 commands, required revisions on update, and required `--ack-irreversible` for delete.
- Validation: focused Resource Types V2 command tests plus docs/wrapper/inventory/readme/formatting contract tests.
- References: Bookings Resource Types V2 links in `docs/references.md`.

## 2026-06-25 - Bookings Reader V2 command-surface drift

- Symptom: the full local suite ran 832 tests with one failure because the parser exposed `bookings-reader-v2 query-extended-bookings` and `bookings-reader-v2 count-extended-bookings`, but the docs/wrapper command-surface contract did not expect them.
- Root cause: the Bookings Reader V2 commands were already implemented and documented in most places, but the public skill wrapper and expected command list lagged behind.
- Fix: kept the commands shipped, added them to `skills/wix/SKILL.md`, added them to the wrapper command-surface contract, and refreshed proof/workspace notes.
- Validation: `.venv/bin/python -m unittest -q tests.test_bookings_reader_v2_commands tests.test_docs_and_skill_wrapper tests.test_official_inventory` passed with 81 tests; `.venv/bin/python -m unittest -q` passed with 832 tests.
- References: Bookings Reader V2 links in `docs/references.md`.

## 2026-06-24 - Bookings Reader V2 shipped as read-only query/count

- Symptom: Wix Bookings Reader V2 is useful for reviewing bookings, but the official current surface does not expose a simple get-by-id method.
- Root cause: Wix documents query and count methods for extended bookings, with single-booking lookup handled through query filters.
- Fix: shipped explicit read-only commands for query and count only, kept Wix Bookings install and permission notes in docs, and kept the family live-unverified.
- Validation: focused command tests and the 2026-06-25 full-suite rerun.
- References: Bookings Reader V2 links in `docs/references.md`.
