# Quickstart (foundation slice)

1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2) Create an environment file and copy template values

```bash
cp .env.example .env
```

3) Start the onboarding flow (creates/updates `.env` and shows required fields)

```bash
google-business-profile-safe-cli --output json onboarding
```

4) Run Google OAuth login

```bash
google-business-profile-safe-cli --output json auth login --console --client-secrets-file /path/to/client-secrets.json
```

5) Verify auth state

```bash
google-business-profile-safe-cli --output json auth check
```

6) Run first read-only API-family commands

```bash
google-business-profile-safe-cli --output json account-management accounts list --parent-account accounts/123
google-business-profile-safe-cli --output json business-info accounts locations list --parent accounts/123 --read-mask "title,primaryPhone"
google-business-profile-safe-cli --output json business-info locations get --name locations/abc --read-mask "name,storeCode"
google-business-profile-safe-cli --output json business-info attributes list --parent locations/abc
google-business-profile-safe-cli --output json business-info categories batch-get --names categories/coffee --language-code en --view BASIC
google-business-profile-safe-cli --output json business-info chains get --name chains/coffee-chain
google-business-profile-safe-cli --output json business-info locations attributes get-google-updated --name locations/abc/attributes
google-business-profile-safe-cli --output json verifications locations fetch-verification-options --location locations/abc --language-code en-US --context-file /path/to/context.json
google-business-profile-safe-cli --output json business-calls locations get-business-calls-settings --name locations/abc/businesscallssettings
google-business-profile-safe-cli --output json verifications locations get-voice-of-merchant-state --name locations/abc
google-business-profile-safe-cli --output json business-calls locations business-calls-insights list --parent locations/abc --filter "metric=CALLS_ANSWERED"
google-business-profile-safe-cli --output json verifications locations verifications list --parent locations/abc --page-size 20
google-business-profile-safe-cli --output json place-actions locations place-action-links list --parent locations/abc --filter "placeActionType=DINING_RESERVATION"
google-business-profile-safe-cli --output json place-actions place-action-type-metadata list --language-code en-US --page-size 20
google-business-profile-safe-cli --output json lodging locations get-lodging --name locations/abc/lodging --read-mask "name,roomCount"
google-business-profile-safe-cli --output json lodging locations lodging get-google-updated --name locations/abc/lodging --read-mask "googleUpdated"
google-business-profile-safe-cli --output json performance locations fetch-multi-daily-metrics-time-series --location locations/abc --daily-metrics DAILY_ORDERS DAILY_CALLS --daily-range-start-year 2025 --daily-range-start-month 1 --daily-range-start-day 1 --daily-range-end-year 2025 --daily-range-end-month 1 --daily-range-end-day 31
google-business-profile-safe-cli --output json performance locations get-daily-metrics-time-series --name locations/abc --daily-metric DAILY_ORDERS --daily-range-start-year 2025 --daily-range-start-month 1 --daily-range-start-day 1 --daily-range-end-year 2025 --daily-range-end-month 1 --daily-range-end-day 31
google-business-profile-safe-cli --output json performance locations search-keywords impressions monthly list --parent locations/abc --monthly-range-start-year 2025 --monthly-range-start-month 1 --monthly-range-end-year 2025 --monthly-range-end-month 3
```

7) Run write command examples (safe dry-run by default)

Keep using the dry-run examples for review. The `--apply` examples require explicit no-snapshot
approval when no saved snapshot is available, and approved applies must produce receipts that record
the approval and recovery limits.

```bash
google-business-profile-safe-cli --output json \
  --plan-out /tmp/location.patch.plan.json \
  business-info locations patch \
  --name locations/abc \
  --update-mask title,storeCode \
  --location-file /path/to/location.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/location.patch.plan.json \
  --receipt-out /tmp/location.patch.receipt.json \
  business-info locations patch \
  --name locations/abc \
  --update-mask title,storeCode \
  --location-file /path/to/location.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/location.create.plan.json \
  business-info accounts locations create \
  --parent accounts/123 \
  --location-file /path/to/location.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/location.create.plan.json \
  --receipt-out /tmp/location.create.receipt.json \
  business-info accounts locations create \
  --parent accounts/123 \
  --location-file /path/to/location.json
```

If you use `--request-id` for create, keep the same value in both the dry-run plan step and the apply step.

```bash
google-business-profile-safe-cli --output json \
  --plan-out /tmp/location.attributes.plan.json \
  business-info locations update-attributes \
  --name locations/abc/attributes \
  --attribute-mask attributes/takeout \
  --attributes-file /path/to/attributes.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/location.attributes.plan.json \
  --receipt-out /tmp/location.attributes.receipt.json \
  business-info locations update-attributes \
  --name locations/abc/attributes \
  --attribute-mask attributes/takeout \
  --attributes-file /path/to/attributes.json

google-business-profile-safe-cli --output json \
  notifications accounts get-notification-setting \
  --name accounts/123/notificationSetting

google-business-profile-safe-cli --output json \
  --plan-out /tmp/notifications.plan.json \
  notifications accounts update-notification-setting \
  --name accounts/123/notificationSetting \
  --notification-setting-file /path/to/notification_setting.json \
  --update-mask emailNotifications

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/notifications.plan.json \
  --receipt-out /tmp/notifications.receipt.json \
  notifications accounts update-notification-setting \
  --name accounts/123/notificationSetting \
  --notification-setting-file /path/to/notification_setting.json \
  --update-mask emailNotifications

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_invitation_accept.plan.json \
  account-management accounts invitations accept \
  --name accounts/123/invitations/inv-001

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_invitation_accept.plan.json \
  --yes \
  --receipt-out /tmp/account_management_invitation_accept.receipt.json \
  account-management accounts invitations accept \
  --name accounts/123/invitations/inv-001

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_invitation_decline.plan.json \
  account-management accounts invitations decline \
  --name accounts/123/invitations/inv-001

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_invitation_decline.plan.json \
  --yes \
  --receipt-out /tmp/account_management_invitation_decline.receipt.json \
  account-management accounts invitations decline \
  --name accounts/123/invitations/inv-001

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_accounts_create.plan.json \
  account-management accounts create \
  --account-file /path/to/account.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_accounts_create.plan.json \
  --receipt-out /tmp/account_management_accounts_create.receipt.json \
  account-management accounts create \
  --account-file /path/to/account.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_accounts_patch.plan.json \
  account-management accounts patch \
  --name accounts/123 \
  --update-mask accountName \
  --account-file /path/to/account.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_accounts_patch.plan.json \
  --receipt-out /tmp/account_management_accounts_patch.receipt.json \
  account-management accounts patch \
  --name accounts/123 \
  --update-mask accountName \
  --account-file /path/to/account.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_accounts_admins_create.plan.json \
  account-management accounts admins create \
  --parent accounts/123 \
  --admin-file /path/to/account_admin.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_accounts_admins_create.plan.json \
  --yes \
  --receipt-out /tmp/account_management_accounts_admins_create.receipt.json \
  account-management accounts admins create \
  --parent accounts/123 \
  --admin-file /path/to/account_admin.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_accounts_admins_patch.plan.json \
  account-management accounts admins patch \
  --name accounts/123/admins/admin-456 \
  --update-mask role \
  --admin-file /path/to/account_admin.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_accounts_admins_patch.plan.json \
  --yes \
  --receipt-out /tmp/account_management_accounts_admins_patch.receipt.json \
  account-management accounts admins patch \
  --name accounts/123/admins/admin-456 \
  --update-mask role \
  --admin-file /path/to/account_admin.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_accounts_admins_delete.plan.json \
  account-management accounts admins delete \
  --name accounts/123/admins/admin-456

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_accounts_admins_delete.plan.json \
  --yes \
  --receipt-out /tmp/account_management_accounts_admins_delete.receipt.json \
  account-management accounts admins delete \
  --name accounts/123/admins/admin-456

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_locations_admins_create.plan.json \
  account-management locations admins create \
  --parent locations/abc \
  --admin-file /path/to/location_admin.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_locations_admins_create.plan.json \
  --yes \
  --receipt-out /tmp/account_management_locations_admins_create.receipt.json \
  account-management locations admins create \
  --parent locations/abc \
  --admin-file /path/to/location_admin.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_locations_admins_patch.plan.json \
  account-management locations admins patch \
  --name locations/abc/admins/admin-456 \
  --update-mask role \
  --admin-file /path/to/location_admin.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_locations_admins_patch.plan.json \
  --yes \
  --receipt-out /tmp/account_management_locations_admins_patch.receipt.json \
  account-management locations admins patch \
  --name locations/abc/admins/admin-456 \
  --update-mask role \
  --admin-file /path/to/location_admin.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_locations_admins_delete.plan.json \
  account-management locations admins delete \
  --name locations/abc/admins/admin-456

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_locations_admins_delete.plan.json \
  --yes \
  --receipt-out /tmp/account_management_locations_admins_delete.receipt.json \
  account-management locations admins delete \
  --name locations/abc/admins/admin-456

google-business-profile-safe-cli --output json \
  --plan-out /tmp/account_management_locations_transfer.plan.json \
  account-management locations transfer \
  --name locations/abc \
  --source-account accounts/111 \
  --destination-account accounts/222

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/account_management_locations_transfer.plan.json \
  --yes \
  --ack-irreversible \
  --receipt-out /tmp/account_management_locations_transfer.receipt.json \
  account-management locations transfer \
  --name locations/abc \
  --source-account accounts/111 \
  --destination-account accounts/222

For `account-management accounts create`, the account file should use an owner resource name and a supported createable type, for example:
`{"accountName":"Example Account","primaryOwner":"accounts/999","type":"LOCATION_GROUP"}`.
For `account-management accounts patch`, keep the file to `{"accountName":"New Name"}` or include a matching `name`.
For `account-management accounts admins create`, use an invitee email in the admin JSON, for example:
`{"admin":"owner@example.com","role":"OWNER"}`.
For `account-management accounts admins create` and `patch`, use only `OWNER` or `MANAGER` roles and avoid `SITE_MANAGER` and `PRIMARY_OWNER`.
For `account-management locations admins create`, use exactly one identity field: either `admin` or `account`.
Examples:
`{"admin":"owner@example.com","role":"OWNER"}` or `{"account":"accounts/999","role":"SITE_MANAGER"}`.
For `account-management locations admins patch`, use only `OWNER`, `MANAGER`, or `SITE_MANAGER` with `"role"` in `--update-mask`.
For `account-management locations transfer`, `--source-account` and `--destination-account` must be different accounts.

google-business-profile-safe-cli --output json \
  --plan-out /tmp/verifications.verify.plan.json \
  verifications locations verify \
  --name locations/abc \
  --method ADDRESS \
  --verification-token-file /path/to/verification-token.json \
  --trusted-partner-token-file /path/to/trusted-partner-token.txt

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/verifications.verify.plan.json \
  --receipt-out /tmp/verifications.verify.receipt.json \
  verifications locations verify \
  --name locations/abc \
  --method ADDRESS \
  --verification-token-file /path/to/verification-token.json \
  --trusted-partner-token-file /path/to/trusted-partner-token.txt

google-business-profile-safe-cli --output json \
  --plan-out /tmp/verifications.verification_tokens.generate.plan.json \
  verifications verification-tokens generate \
  --location-id 123456

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/verifications.verification_tokens.generate.plan.json \
  verifications verification-tokens generate \
  --location-id 123456 \
  --verification-token-out /tmp/verification-token.json \
  --receipt-out /tmp/verifications.verification_tokens.generate.receipt.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/verifications.complete.plan.json \
  verifications locations verifications complete \
  --name locations/abc/verifications/verify-001 \
  --pin-file /path/to/verification-pin.txt

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/verifications.complete.plan.json \
  --receipt-out /tmp/verifications.complete.receipt.json \
  verifications locations verifications complete \
  --name locations/abc/verifications/verify-001 \
  --pin-file /path/to/verification-pin.txt

google-business-profile-safe-cli --output json \
  --plan-out /tmp/place_action_links.create.plan.json \
  place-actions locations place-action-links create \
  --parent locations/abc \
  --place-action-link-file /path/to/place_action_link.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/place_action_links.create.plan.json \
  --receipt-out /tmp/place_action_links.create.receipt.json \
  place-actions locations place-action-links create \
  --parent locations/abc \
  --place-action-link-file /path/to/place_action_link.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/place_action_links.patch.plan.json \
  place-actions locations place-action-links patch \
  --name locations/abc/placeActionLinks/xyz \
  --update-mask uri \
  --place-action-link-file /path/to/place_action_link.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/place_action_links.patch.plan.json \
  --receipt-out /tmp/place_action_links.patch.receipt.json \
  place-actions locations place-action-links patch \
  --name locations/abc/placeActionLinks/xyz \
  --update-mask uri \
  --place-action-link-file /path/to/place_action_link.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/place_action_links.delete.plan.json \
  place-actions locations place-action-links delete \
  --name locations/abc/placeActionLinks/xyz

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/place_action_links.delete.plan.json \
  --yes \
  --receipt-out /tmp/place_action_links.delete.receipt.json \
  place-actions locations place-action-links delete \
  --name locations/abc/placeActionLinks/xyz

google-business-profile-safe-cli --output json \
  --plan-out /tmp/business_calls_settings_update.plan.json \
  business-calls locations update-business-calls-settings \
  --name locations/abc/businesscallssettings \
  --update-mask businessCallsEnabled \
  --business-calls-settings-file /path/to/business_calls_settings.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/business_calls_settings_update.plan.json \
  --receipt-out /tmp/business_calls_settings_update.receipt.json \
  business-calls locations update-business-calls-settings \
  --name locations/abc/businesscallssettings \
  --update-mask businessCallsEnabled \
  --business-calls-settings-file /path/to/business_calls_settings.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/media_upload.plan.json \
  media-upload-v1 media upload \
  --resource-name locations/123/media/abc \
  --media-json-file /path/to/media.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/media_upload.plan.json \
  --receipt-out /tmp/media_upload.receipt.json \
  media-upload-v1 media upload \
  --resource-name locations/123/media/abc \
  --media-json-file /path/to/media.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/media_upload_file.plan.json \
  media-upload-v1 media upload \
  --resource-name locations/123/media/abc \
  --media-file /path/to/photo.png
```

The `media-upload-v1` command covers the official upload step itself.
The focused legacy follow-up around that upload step is now:

```bash
google-business-profile-safe-cli --output json \
  --plan-out /tmp/legacy_media_start_upload.plan.json \
  legacy-v49 accounts locations media start-upload \
  --parent accounts/123/locations/456

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/legacy_media_start_upload.plan.json \
  --receipt-out /tmp/legacy_media_start_upload.receipt.json \
  legacy-v49 accounts locations media start-upload \
  --parent accounts/123/locations/456

google-business-profile-safe-cli --output json \
  --plan-out /tmp/legacy_media_create.plan.json \
  legacy-v49 accounts locations media create \
  --parent accounts/123/locations/456 \
  --media-item-file /path/to/media_item.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/legacy_media_create.plan.json \
  --receipt-out /tmp/legacy_media_create.receipt.json \
  legacy-v49 accounts locations media create \
  --parent accounts/123/locations/456 \
  --media-item-file /path/to/media_item.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/legacy_location_transfer.plan.json \
  legacy-v49 accounts locations transfer \
  --name accounts/123/locations/456 \
  --to-account accounts/999

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/legacy_location_transfer.plan.json \
  --yes \
  --ack-irreversible \
  --receipt-out /tmp/legacy_location_transfer.receipt.json \
  legacy-v49 accounts locations transfer \
  --name accounts/123/locations/456 \
  --to-account accounts/999

cat > /tmp/review_reply.json <<'JSON'
{"comment":"Thanks for your feedback."}
JSON

google-business-profile-safe-cli --output json \
  legacy-v49 accounts locations reviews list \
  --parent accounts/123/locations/456 \
  --page-size 20 \
  --order-by "rating desc"

google-business-profile-safe-cli --output json \
  legacy-v49 accounts locations reviews get \
  --name accounts/123/locations/456/reviews/review-123

google-business-profile-safe-cli --output json \
  --plan-out /tmp/legacy_review_reply.plan.json \
  legacy-v49 accounts locations reviews update-reply \
  --name accounts/123/locations/456/reviews/review-123 \
  --reply-file /tmp/review_reply.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/legacy_review_reply.plan.json \
  --receipt-out /tmp/legacy_review_reply.receipt.json \
  legacy-v49 accounts locations reviews update-reply \
  --name accounts/123/locations/456/reviews/review-123 \
  --reply-file /tmp/review_reply.json

google-business-profile-safe-cli --output json \
  --plan-out /tmp/legacy_review_reply_delete.plan.json \
  legacy-v49 accounts locations reviews delete-reply \
  --name accounts/123/locations/456/reviews/review-123

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/legacy_review_reply_delete.plan.json \
  --yes \
  --receipt-out /tmp/legacy_review_reply_delete.receipt.json \
  legacy-v49 accounts locations reviews delete-reply \
  --name accounts/123/locations/456/reviews/review-123

google-business-profile-safe-cli --output json \
  --plan-out /tmp/lodging_update.plan.json \
  lodging locations update-lodging \
  --name locations/abc/lodging \
  --update-mask "roomCount" \
  --lodging-file /path/to/lodging.json

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/lodging_update.plan.json \
  --receipt-out /tmp/lodging_update.receipt.json \
  lodging locations update-lodging \
  --name locations/abc/lodging \
  --update-mask "roomCount" \
  --lodging-file /path/to/lodging.json
```

Location delete is destructive and must use follow-up verification:

```bash
google-business-profile-safe-cli --output json \
  --plan-out /tmp/location.delete.plan.json \
  business-info locations delete \
  --name locations/abc

google-business-profile-safe-cli --output json --apply \
  --plan-in /tmp/location.delete.plan.json \
  --yes --ack-irreversible \
  --receipt-out /tmp/location.delete.receipt.json \
  business-info locations delete \
  --name locations/abc
```

For `update-attributes`, the JSON file should be an `Attributes` object such as
`{"name":"locations/abc/attributes","attributes":[{"name":"attributes/takeout","values":[true]}]}`.
For `update-business-calls-settings`, use a `BusinessCallsSettings` object with `name` and the fields you want to update.
`account-management accounts invitations accept/decline` are account-access state changes and require `--plan-in` and `--yes` when applying.
Performance commands in this slice are read-only and do not require plan/receipt apply flow.
For `verification-token-file`, use a `VerificationToken` JSON object such as
`{"tokenString":"BASE64_TOKEN"}`.
For `verifications verification-tokens generate`, pass `--location-id` (numeric location id), use a dry-run plan first, then `--apply --verification-token-out`.
This method is discovery-backed and has no separate read-back command; success is validated from response fields (`result` and optional `instantVerificationToken`).
`verifications locations verify` requires a matching dry-run apply plan and verifies completion by checking the created verification appears in the parent `verifications list`.
`verifications locations verifications complete` requires a matching dry-run apply plan and verifies completion by checking that verification is returned with state `COMPLETED`.

If delete verification reports `not_found`, this is the expected successful verification result.
If it still returns a location, the receipt should mark that verification as failed.
Media upload verification in this slice has no direct read-back command, so success is currently verified by matching `response.resourceName` to the requested resource.
Legacy media follow-up verification in this slice has no direct read-back command either, so success is currently verified by the returned `mediaItemDataRef`, `dataRef.resourceName`, `resourceName`, or `sourceUrl` when the provider echoes one back.
Legacy review reply update verification is strict read-back verification through `legacy-v49 accounts locations reviews get` and matching `reviewReply.comment`.
Legacy review reply delete verification is strict read-back verification through `legacy-v49 accounts locations reviews get` and absence of `reviewReply`.
Business-calls write verification is strict read-back verified through `business-calls locations get-business-calls-settings` and matching returned `name`.
Lodging write verification is strict read-back verified through `lodging locations get-lodging` and matching returned `name`.

Use `--output json` to keep the safe payload shape:
- `ok`
- `operation`
- `dry_run`
- For reads: `request`, `response`
- For writes:
  - `plan` or `receipt`
  - `plan_path` / `receipt_path` when written

Machine-readable version check:

```bash
google-business-profile-safe-cli --output json --version
```
