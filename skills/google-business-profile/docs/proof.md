# Proof pack

Purpose:
- Record what the current shipped tool proves with local commands.
- Keep this folder honest about current behavior and verification commands.
- You don’t need to run these commands yourself; they are here for auditing and proof.

Rules:
- Never include secrets (tokens, client secrets, Authorization headers).
- Use placeholder values in examples.
- Keep commands and outputs short and factual.

Current Wave 3 safety result: provider write apply requires explicit no-snapshot approval before Google Business Profile HTTP
until per-command before-state capture exists. Dry-run plans still work and include
`before_state.required: true` and `before_state.supported: false`.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: local unit test suite
- Tool version: 0.1.0
- Provider API version: account-management, business-info, business-calls, notifications, media-upload-v1, place-actions, legacy-v49 reviews/verifications/transfer/media follow-up, lodging, performance, and verifications coverage
- Environment: local dev / official Account Management, Business Information, Business Calls, Notifications, Place Actions, Performance, Media upload, legacy v4.9, Lodging, and Verifications API hosts
- API request behavior is tested with mocked provider responses only; no live Google calls in unit tests.
- Old committed mock receipt examples are retained as historical command-shape examples. They are not current successful live-apply promises.
- Latest local validation result:
- `.venv/bin/python -m unittest -q tests/test_api_client.py tests/test_official_inventory.py tests/test_legacy_v49_verifications_commands.py` with **58 passing tests**
- `.venv/bin/python -m unittest -q` with **314 passing tests**
- JSON validation for `docs/official_inventory.json` plus **79** committed example output JSON files (**80 files total**)

## Smoke checks (copy/paste)

Run in the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`
- `.venv/bin/python -m unittest -q`

2) Version (no `.env` required):
- `google-business-profile-safe-cli --output json --version`

3) Auth/config check (read-only):
- `google-business-profile-safe-cli --output json auth check`

4) Token helpers:
- `google-business-profile-safe-cli --output json auth token status`

5) First API-family smoke checks (representative):
- `google-business-profile-safe-cli --output json account-management accounts list --parent-account accounts/123`
- `google-business-profile-safe-cli --output json business-info accounts locations list --parent accounts/123 --read-mask "name"`

6) Full shipped coverage is in unit tests (mocked provider responses) for all of:
- `account-management accounts list`
- `account-management accounts get`
- `account-management accounts admins list`
- `account-management accounts invitations list`
- `account-management locations admins list`
- `account-management accounts admins create` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by listing admins)
- `account-management accounts admins delete` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by listing admins)
- `account-management accounts admins patch` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by listing admins)
- `account-management locations admins create` (dry-run, `--apply` + `--plan-in` + `--yes`, with both invitee/email and account identity mode coverage)
- `account-management locations admins delete` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by listing admins)
- `account-management locations admins patch` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by listing admins)
- `account-management locations transfer` (dry-run, `--apply` + `--plan-in` + `--yes` + `--ack-irreversible`; follow-up verification by checking source/destination location lists)
- `business-info accounts locations list`
- `business-info locations get`
- `business-info locations get-attributes`
- `business-info locations get-google-updated`
- `business-info locations attributes get-google-updated`
- `business-info attributes list`
- `business-info categories list`
- `business-info categories batch-get`
- `business-info chains search`
- `business-info chains get`
- `business-info google-locations search`
- `business-info locations patch` (default dry-run, with optional `--validate-only`)
- `business-info locations patch` (`--apply` + `--plan-in`)
- `business-info locations update-attributes` (dry-run and `--apply` + `--plan-in`)
- `business-info accounts locations create` (dry-run, optional `--validate-only`, `--apply` + `--plan-in`)
- `business-info locations delete` (dry-run, and `--apply` + `--plan-in` + `--yes` + `--ack-irreversible` with follow-up verification)
- `account-management accounts invitations accept` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by checking the invitation disappears)
- `account-management accounts invitations decline` (dry-run, `--apply` + `--plan-in` + `--yes`, and follow-up verification by checking the invitation disappears)
- `account-management accounts create` (dry-run, `--apply` + `--plan-in`, and follow-up verification by reading back the created account)
- `account-management accounts patch` (dry-run, `--apply` + `--plan-in`, and follow-up verification by reading back the account)
- `notifications accounts get-notification-setting`
- `notifications accounts update-notification-setting` (dry-run, `--apply` + `--plan-in`, and plan-in mismatch refusal)
- `media-upload-v1 media upload --media-json-file` (dry-run and `--apply` + `--plan-in`)
- `media-upload-v1 media upload --media-file` (dry-run and `--apply` + `--plan-in`)
- `legacy-v49 accounts locations reviews list` (`read`)
- `legacy-v49 accounts locations reviews get` (`read`)
- `legacy-v49 accounts locations reviews update-reply` (dry-run, `--apply` + `--plan-in`, and read-back verification that `reviewReply.comment` matches)
- `legacy-v49 accounts locations reviews delete-reply` (dry-run, `--apply` + `--plan-in` + `--yes`, and read-back verification that `reviewReply` is absent)
- `legacy-v49 accounts locations verifications list` (`read`)
- `legacy-v49 accounts locations verifications complete` (`write`; dry-run + `--apply` + `--plan-in`; strict follow-up by listing parent location verifications and checking `COMPLETED`)
- `legacy-v49 accounts locations transfer` (dry-run, `--apply` + `--plan-in` + `--yes` + `--ack-irreversible`, and read-back verification against source/destination account location lists)
- `legacy-v49 accounts locations media start-upload` (dry-run and `--apply` + `--plan-in`)
- `legacy-v49 accounts locations media create` (dry-run, `--apply` + `--plan-in`, and plan-in mismatch refusal)
- `lodging locations get-lodging` (`read`)
- `lodging locations update-lodging` (dry-run, `--apply` + `--plan-in`, with read-back verification)
- `lodging locations lodging get-google-updated` (`read`)
- `business-calls locations get-business-calls-settings` (`read`)
- `business-calls locations update-business-calls-settings` (dry-run, `--apply` + `--plan-in`, with read-back verification)
- `business-calls locations business-calls-insights list` (`read`)
- `performance locations fetch-multi-daily-metrics-time-series` (`read`)
- `performance locations get-daily-metrics-time-series` (`read`)
- `performance locations search-keywords impressions monthly list` (`read`)
- `place-actions locations place-action-links create` (dry-run, `--apply` + `--plan-in`, with read-back verification)
- `place-actions locations place-action-links delete` (dry-run, `--apply` + `--plan-in` + `--yes` with read-back 404 verification)
- `place-actions locations place-action-links get` (`read`)
- `place-actions locations place-action-links list` (`read`)
- `place-actions locations place-action-links patch` (dry-run, `--apply` + `--plan-in`, with read-back verification)
- `place-actions place-action-type-metadata list` (`read`)
- The upload sequence now covers the official upload step plus the focused legacy media follow-up that creates the location media record around it.
- `verifications locations fetch-verification-options` (`read`)
- `verifications locations get-voice-of-merchant-state` (`read`)
- `verifications locations verifications list` (`read`)
- `verifications locations verify` (`write`; dry-run + `--apply + --plan-in`, strict follow-up by listing parent location verifications)
- `verifications locations verifications complete` (`write`; dry-run + `--apply + --plan-in`, strict follow-up by listing parent location verifications and checking `COMPLETED`)
- `verifications verification-tokens generate` (`write`; dry-run + `--apply + --plan-in`; response-derived success when `result == SUCCEEDED`)

7) Modern account-management transfer and legacy-v49 location-transfer write surfaces are now implemented.

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/account_management_accounts_list.mock.json`
- `docs/examples/outputs/account_management_accounts_invitations_accept_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_invitations_accept_receipt.mock.json`
- `docs/examples/outputs/account_management_accounts_invitations_decline_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_invitations_decline_receipt.mock.json`
- `docs/examples/outputs/account_management_accounts_create_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_create_receipt.mock.json`
- `docs/examples/outputs/account_management_accounts_admins_create_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_admins_create_receipt.mock.json`
- `docs/examples/outputs/account_management_accounts_admins_delete_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_admins_delete_receipt.mock.json`
- `docs/examples/outputs/account_management_accounts_admins_patch_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_admins_patch_receipt.mock.json`
- `docs/examples/outputs/account_management_locations_admins_create_plan.mock.json`
- `docs/examples/outputs/account_management_locations_admins_create_receipt.mock.json`
- `docs/examples/outputs/account_management_locations_admins_delete_plan.mock.json`
- `docs/examples/outputs/account_management_locations_admins_delete_receipt.mock.json`
- `docs/examples/outputs/account_management_locations_admins_patch_plan.mock.json`
- `docs/examples/outputs/account_management_locations_admins_patch_receipt.mock.json`
- `docs/examples/outputs/account_management_locations_transfer_plan.mock.json`
- `docs/examples/outputs/account_management_locations_transfer_receipt.mock.json`
- `docs/examples/outputs/account_management_accounts_patch_plan.mock.json`
- `docs/examples/outputs/account_management_accounts_patch_receipt.mock.json`
- `docs/examples/outputs/business_info_accounts_locations_create_plan.mock.json`
- `docs/examples/outputs/business_info_locations_get.mock.json`
- `docs/examples/outputs/business_info_categories_batch_get.mock.json`
- `docs/examples/outputs/business_info_chains_get.mock.json`
- `docs/examples/outputs/business_info_locations_attributes_get_google_updated.mock.json`
- `docs/examples/outputs/business_info_locations_patch_plan.mock.json`
- `docs/examples/outputs/business_info_locations_update_attributes_receipt.mock.json`
- `docs/examples/outputs/business_info_locations_delete_plan.mock.json`
- `docs/examples/outputs/lodging_locations_get_lodging.mock.json`
- `docs/examples/outputs/lodging_locations_update_lodging_plan.mock.json`
- `docs/examples/outputs/lodging_locations_update_lodging_receipt.mock.json`
- `docs/examples/outputs/lodging_locations_lodging_get_google_updated.mock.json`
- `docs/examples/outputs/business_calls_locations_get_business_calls_settings.mock.json`
- `docs/examples/outputs/business_calls_locations_update_business_calls_settings_plan.mock.json`
- `docs/examples/outputs/business_calls_locations_update_business_calls_settings_receipt.mock.json`
- `docs/examples/outputs/business_calls_locations_business_calls_insights_list.mock.json`
- `docs/examples/outputs/notifications_accounts_get_notification_setting.mock.json`
- `docs/examples/outputs/notifications_accounts_update_notification_setting_plan.mock.json`
- `docs/examples/outputs/notifications_accounts_update_notification_setting_receipt.mock.json`
- `docs/examples/outputs/media_upload_v1_media_upload_plan.mock.json`
- `docs/examples/outputs/media_upload_v1_media_upload_receipt.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_reviews_list.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_reviews_get.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_reviews_update_reply_plan.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_reviews_update_reply_receipt.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_reviews_delete_reply_plan.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_reviews_delete_reply_receipt.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_verifications_list.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_verifications_complete_plan.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_verifications_complete_receipt.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_transfer_plan.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_transfer_receipt.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_media_start_upload_receipt.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_media_start_upload_plan.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_media_create_plan.mock.json`
- `docs/examples/outputs/legacy_v49_accounts_locations_media_create_receipt.mock.json`
- `docs/examples/outputs/performance_locations_fetch_multi_daily_metrics_time_series.mock.json`
- `docs/examples/outputs/performance_locations_get_daily_metrics_time_series.mock.json`
- `docs/examples/outputs/performance_locations_search_keywords_impressions_monthly_list.mock.json`
- `docs/examples/outputs/place_actions_locations_place_action_links_create_plan.mock.json`
- `docs/examples/outputs/place_actions_locations_place_action_links_delete_plan.mock.json`
- `docs/examples/outputs/place_actions_locations_place_action_links_get.mock.json`
- `docs/examples/outputs/place_actions_locations_place_action_links_list.mock.json`
- `docs/examples/outputs/place_actions_locations_place_action_links_patch_plan.mock.json`
- `docs/examples/outputs/place_actions_place_action_type_metadata_list.mock.json`
- `docs/examples/outputs/verifications_locations_fetch_verification_options.mock.json`
- `docs/examples/outputs/verifications_locations_get_voice_of_merchant_state.mock.json`
- `docs/examples/outputs/verifications_locations_verifications_list.mock.json`
- `docs/examples/outputs/verifications_locations_verify_plan.mock.json`
- `docs/examples/outputs/verifications_locations_verify_receipt.mock.json`
- `docs/examples/outputs/verifications_locations_verifications_complete_plan.mock.json`
- `docs/examples/outputs/verifications_locations_verifications_complete_receipt.mock.json`
- `docs/examples/outputs/verifications_verification_tokens_generate_plan.mock.json`
- `docs/examples/outputs/verifications_verification_tokens_generate_receipt.mock.json`

## What can go wrong (and how we verify)

- **Missing or unreadable OAuth config** → confirm `auth check` reports `ok=false` and update `.env`.
- **Missing token file** → confirm `auth token status` shows `exists=false`, then run `auth login` or `auth token set`.
- **Invalid token state** → confirm token status and re-authenticate with `auth login`.
- **Unsupported API commands** → this folder intentionally exposes only listed `account-management`, `business-info`, `notifications`, `media-upload-v1`, `place-actions`, current legacy-v49 reviews/verifications/transfer/media follow-up, `lodging`, `performance`, `verifications`, auth, and runs tooling commands.
- **Legacy review reply writes** → `update-reply` reads the review back and matches `reviewReply.comment`; `delete-reply` reads the review back and expects `reviewReply` to be absent before marking `changed=true`.
- **Legacy verification completion** → completion writes are planned first, use `--pin-file` instead of a raw PIN flag, and only mark `changed=true` after the parent location verification list shows the same verification in `COMPLETED` state.
- **Media upload flow expectations** → the tool covers the official upload step plus the focused legacy follow-up that starts the upload and creates the location media record. The remaining legacy media read/update/delete commands are still tracked in `docs/api_coverage.md`.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
