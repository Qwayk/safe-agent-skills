# Command reference

Use this page when you need the exact Google Business Profile command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `google-business-profile-safe-cli onboarding [--no-write-env]`

## Auth

- `google-business-profile-safe-cli auth login [--client-secrets-file ...] [--scopes ...] [--console] [--port 0]`
- `google-business-profile-safe-cli auth check`
- `google-business-profile-safe-cli auth token set --file token.json`
- `google-business-profile-safe-cli auth token status`

## Account Management (read/write slice)

- `google-business-profile-safe-cli account-management accounts list [--parent-account ...] [--page-size ...] [--page-token ...] [--filter ...]`
- `google-business-profile-safe-cli account-management accounts get --name <accounts/{account}>`
- `google-business-profile-safe-cli account-management accounts create --account-file <path>`
- `google-business-profile-safe-cli account-management accounts patch --name <accounts/{account}> --update-mask <field,...> --account-file <path> [--validate-only]`
- `google-business-profile-safe-cli account-management accounts admins list --parent <accounts/{account}>`
- `google-business-profile-safe-cli account-management accounts admins create --parent <accounts/{account}> --admin-file <path>`
- `google-business-profile-safe-cli account-management accounts admins delete --name <accounts/{account}/admins/{admin}>`
- `google-business-profile-safe-cli account-management accounts admins patch --name <accounts/{account}/admins/{admin}> --update-mask <field,...> --admin-file <path>`
- `google-business-profile-safe-cli account-management locations admins create --parent <locations/{location}> --admin-file <path>`
- `google-business-profile-safe-cli account-management locations admins delete --name <locations/{location}/admins/{admin}>`
- `google-business-profile-safe-cli account-management locations admins patch --name <locations/{location}/admins/{admin}> --update-mask <field,...> --admin-file <path>`
- `google-business-profile-safe-cli account-management locations transfer --name <locations/{location}> --source-account <accounts/{account}> --destination-account <accounts/{account}>`
- `google-business-profile-safe-cli account-management accounts invitations accept --name <accounts/{account}/invitations/{invitation}>`
- `google-business-profile-safe-cli account-management accounts invitations decline --name <accounts/{account}/invitations/{invitation}>`
- `google-business-profile-safe-cli account-management accounts invitations list --parent <accounts/{account}> [--filter ...]`
- `google-business-profile-safe-cli account-management locations admins list --parent <locations/{location}>`

For `account-management accounts create`, the `Account` JSON should use `primaryOwner` as a resource name like `accounts/999` and `type` as `LOCATION_GROUP` or `USER_GROUP`.
For `account-management accounts patch`, `--update-mask` is required and this CLI currently supports only `accountName`. If you include `name` in the JSON file, it must match `--name`.
For `account-management accounts admins create`, use the invitee email address in `admin` and use only `OWNER` or `MANAGER` in `role`.
`SITE_MANAGER` and `PRIMARY_OWNER` are rejected in this slice.
For `account-management locations admins create`, use exactly one identity shape: either
`admin` as invitee email or `account` as `accounts/{account}`. `OWNER`, `MANAGER`, and `SITE_MANAGER` are allowed.
`PRIMARY_OWNER` and `ADMIN_ROLE_UNSPECIFIED` are rejected in this slice.
For `account-management locations transfer`, include both required accounts with `--source-account` and `--destination-account`, make sure they are different accounts, then use `--plan-out` for dry-run and `--apply --plan-in --yes --ack-irreversible` for write execution.
For `account-management accounts admins patch`, this CLI supports only `role` in `--update-mask`.
For `account-management locations admins patch`, this CLI supports only `role` in `--update-mask`.
If `name` is included in `--admin-file`, it must match `--name`.

## Business Information (read-only and write slice)

- `google-business-profile-safe-cli business-info accounts locations list --parent <accounts/{account}> --read-mask <mask> [--page-size ...] [--page-token ...] [--filter ...] [--order-by ...]`
- `google-business-profile-safe-cli business-info accounts locations create --parent <accounts/{account}> --location-file <path-to-json-Location-object> [--validate-only] [--request-id <id>]`
- `google-business-profile-safe-cli business-info locations get --name <locations/{location}> --read-mask <mask>`
- `google-business-profile-safe-cli business-info locations get-attributes --name <locations/{location}/attributes>`
- `google-business-profile-safe-cli business-info locations delete --name <locations/{location}>`
- `google-business-profile-safe-cli business-info locations get-google-updated --name <locations/{location}> --read-mask <mask>`
- `google-business-profile-safe-cli business-info locations attributes get-google-updated --name <locations/{location}/attributes>`
- `google-business-profile-safe-cli business-info attributes list --parent <locations/{location}> | --category-name <categories/{category_id}> --region-code <CC> --language-code <bcp47> | --show-all --region-code <CC> --language-code <bcp47> [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli business-info categories list --region-code <CC> --language-code <bcp47> --view <BASIC|FULL> [--filter ...] [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli business-info categories batch-get --names <categories/{category_id}> --names <categories/{category_id}> [--names ...] --language-code <bcp47> --view <BASIC|FULL> [--region-code <CC>]`
- `google-business-profile-safe-cli business-info chains search --chain-name <name> [--page-size ...]`
- `google-business-profile-safe-cli business-info chains get --name <chains/{chain_place_id}>`
- `google-business-profile-safe-cli business-info google-locations search --query <text> | --location-file <path-to-json-Location-object> [--page-size ...]`
- `google-business-profile-safe-cli business-info locations patch --name <locations/{location}> --update-mask <field,field,...> --location-file <path-to-json-Location-object> [--validate-only]`
- `google-business-profile-safe-cli business-info locations update-attributes --name <locations/{location}/attributes> --attribute-mask <attributes/{attribute},...> --attributes-file <path-to-Attributes-JSON>`
- `google-business-profile-safe-cli business-calls locations get-business-calls-settings --name <locations/{location}/businesscallssettings>`
- `google-business-profile-safe-cli business-calls locations update-business-calls-settings --name <locations/{location}/businesscallssettings> --update-mask <field,field,...> --business-calls-settings-file <path-to-BusinessCallsSettings-JSON>`
- `google-business-profile-safe-cli business-calls locations business-calls-insights list --parent <locations/{location}> [--page-size ...] [--page-token ...] [--filter ...]`
- `google-business-profile-safe-cli place-actions locations place-action-links create --parent <locations/{location}> --place-action-link-file <path>`
- `google-business-profile-safe-cli place-actions locations place-action-links delete --name <locations/{location}/placeActionLinks/{id}>`
- `google-business-profile-safe-cli place-actions locations place-action-links get --name <locations/{location}/placeActionLinks/{id}>`
- `google-business-profile-safe-cli place-actions locations place-action-links list --parent <locations/{location}> [--filter ...] [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli place-actions locations place-action-links patch --name <locations/{location}/placeActionLinks/{id}> --update-mask <field,field,...> --place-action-link-file <path>`
- `google-business-profile-safe-cli place-actions place-action-type-metadata list [--language-code <bcp47>] [--page-size ...] [--page-token ...] [--filter ...]`
- `google-business-profile-safe-cli lodging locations get-lodging --name <locations/{location}/lodging> --read-mask <mask>`
- `google-business-profile-safe-cli lodging locations update-lodging --name <locations/{location}/lodging> --update-mask <field,field,...> --lodging-file <path-to-Lodging-JSON>`
- `google-business-profile-safe-cli lodging locations lodging get-google-updated --name <locations/{location}/lodging> --read-mask <mask>`
- `google-business-profile-safe-cli performance locations fetch-multi-daily-metrics-time-series --location <locations/{location}> --daily-metrics <metric> [<metric> ...] --daily-range-start-year <YYYY> --daily-range-start-month <MM> --daily-range-start-day <DD> --daily-range-end-year <YYYY> --daily-range-end-month <MM> --daily-range-end-day <DD>`
- `google-business-profile-safe-cli performance locations get-daily-metrics-time-series --name <locations/{location}> --daily-metric <metric> --daily-range-start-year <YYYY> --daily-range-start-month <MM> --daily-range-start-day <DD> --daily-range-end-year <YYYY> --daily-range-end-month <MM> --daily-range-end-day <DD>`
- `google-business-profile-safe-cli performance locations search-keywords impressions monthly list --parent <locations/{location}> --monthly-range-start-year <YYYY> --monthly-range-start-month <MM> --monthly-range-end-year <YYYY> --monthly-range-end-month <MM> [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli verifications locations fetch-verification-options --location <locations/{location}> --language-code <bcp47> [--context-file <path-to-ServiceBusinessContext-JSON>]`
- `google-business-profile-safe-cli verifications locations get-voice-of-merchant-state --name <locations/{location}>`
- `google-business-profile-safe-cli verifications locations verifications list --parent <locations/{location}> [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli verifications locations verify --name <locations/{location}> --method <ADDRESS|EMAIL|PHONE_CALL|SMS|AUTO|TRUSTED_PARTNER> [--language-code ...] [--mailer-contact ...] [--phone-number ...] [--email-address ...] [--context-file <ServiceBusinessContext-JSON>] [--verification-token-file <path>] [--trusted-partner-token-file <path>]`
- `google-business-profile-safe-cli verifications locations verifications complete --name <locations/{location}/verifications/{verification}> --pin-file <path-to-pin>`
- `google-business-profile-safe-cli verifications verification-tokens generate --location-id <numeric-location-id> --verification-token-out <path-to-token-file.json>`
- `google-business-profile-safe-cli notifications accounts get-notification-setting --name <accounts/{account}/notificationSetting>`
- `google-business-profile-safe-cli notifications accounts update-notification-setting --name <accounts/{account}/notificationSetting> --notification-setting-file <path-to-NotificationSetting-JSON> --update-mask <field,field,...>`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews list --parent <accounts/{account}/locations/{location}> [--page-size <1-50>] [--page-token <token>] [--order-by <rating|rating desc|updateTime desc>]`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews get --name <accounts/{account}/locations/{location}/reviews/{review}>`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews update-reply --name <accounts/{account}/locations/{location}/reviews/{review}> --reply-file <path-to-ReviewReply-JSON>`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews delete-reply --name <accounts/{account}/locations/{location}/reviews/{review}>`
- `google-business-profile-safe-cli legacy-v49 accounts locations verifications list --parent <accounts/{account}/locations/{location}> [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli legacy-v49 accounts locations verifications complete --name <accounts/{account}/locations/{location}/verifications/{verification}> --pin-file <path-to-pin>`
- `google-business-profile-safe-cli legacy-v49 accounts locations transfer --name <accounts/{account}/locations/{location}> --to-account <accounts/{account}>`
- `google-business-profile-safe-cli media-upload-v1 media upload --resource-name <Google-provided or provider upload resource> [--media-file <path-to-binary>] [--media-json-file <path-to-media-json>] [--content-type <mime>]`
- `google-business-profile-safe-cli legacy-v49 accounts locations media start-upload --parent <accounts/{account}/locations/{location}>`
- `google-business-profile-safe-cli legacy-v49 accounts locations media create --parent <accounts/{account}/locations/{location}> --media-item-file <path-to-MediaItem-JSON>`

Write commands are dry-run only unless `--apply` is set.
For `account-management accounts admins` and `account-management locations admins` `create|delete|patch`, `--apply` also requires `--plan-in` and `--yes`.
For `media-upload-v1 media upload`, use exactly one of `--media-file` or `--media-json-file`.
For `verifications locations verify`, use `--verification-token-file` for `token` values and `--trusted-partner-token-file` for partner token values. For `verifications locations verifications complete`, use `--pin-file` for PIN values.
For `verifications verification-tokens generate`, the command writes the returned token only when `result` is `SUCCEEDED` and stores it as `{"tokenString": "..."}`
in `--verification-token-out` without emitting the raw token in command output.
For binary upload, `--content-type` is optional and inferred from file extension if omitted.
This command covers the official upload step itself. The legacy follow-up flow is now implemented with
`legacy-v49 accounts locations media start-upload` and `legacy-v49 accounts locations media create`.
For `legacy-v49 accounts locations reviews update-reply`, `--reply-file` must be a JSON object with exactly
`{"comment":"..."}`. Apply requires `--plan-in` and verification reads the review back to confirm the reply text matches.
For `legacy-v49 accounts locations reviews delete-reply`, apply requires `--plan-in --yes` and verification reads the review
back to confirm `reviewReply` is absent.
For `legacy-v49 accounts locations verifications complete`, use `--pin-file` so the PIN stays out of shell history. Apply requires
`--plan-in`, and verification lists the parent location verifications and confirms the target verification state is `COMPLETED`.
For `legacy-v49 accounts locations transfer`, use a deprecated legacy location resource name in `--name`, choose a different `--to-account`, and apply only with `--plan-in --yes --ack-irreversible`.
For `business-info locations delete`:
- apply requires `--plan-in`, `--yes`, and `--ack-irreversible`;
- some locations may not allow API deletion and may require deletion from the Google Business Profile website instead.
For write review runs, use `--plan-in` for safety checks where documented and optionally `--plan-out`.
Do not expect a successful provider write receipt until before-state support is added.

## Runs (history)

- `google-business-profile-safe-cli runs list [--limit 20]`
- `google-business-profile-safe-cli runs show --run-id <run_id>`

This tool intentionally exposes no `jobs` or `demo` command families.
