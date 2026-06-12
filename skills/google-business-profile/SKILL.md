# google-business-profile-safe-cli

This page is the agent-facing rule sheet for the public Google Business Profile skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill gives an agent a careful path for Google Business Profile account, location, review, media, verification, and performance work through `google-business-profile-safe-cli`.

## Available commands

- `google-business-profile-safe-cli onboarding`
- `google-business-profile-safe-cli auth login [--console]`
- `google-business-profile-safe-cli auth check`
- `google-business-profile-safe-cli auth token set --file <path>`
- `google-business-profile-safe-cli auth token status`
- `google-business-profile-safe-cli runs list|show`
- `google-business-profile-safe-cli account-management accounts list`
- `google-business-profile-safe-cli account-management accounts get --name <accounts/{account}>`
- `google-business-profile-safe-cli account-management accounts create --account-file <path>`
- `google-business-profile-safe-cli account-management accounts patch --name <accounts/{account}> --update-mask <field,...> --account-file <path>`
- `google-business-profile-safe-cli account-management accounts admins list --parent <accounts/{account}>`
- `google-business-profile-safe-cli account-management accounts admins create --parent <accounts/{account}> --admin-file <path>`
- `google-business-profile-safe-cli account-management accounts admins delete --name <accounts/{account}/admins/{admin}>`
- `google-business-profile-safe-cli account-management accounts admins patch --name <accounts/{account}/admins/{admin}> --update-mask <field,...> --admin-file <path>`
- `google-business-profile-safe-cli account-management accounts invitations accept --name <accounts/{account}/invitations/{invitation}>`
- `google-business-profile-safe-cli account-management accounts invitations decline --name <accounts/{account}/invitations/{invitation}>`
- `google-business-profile-safe-cli account-management accounts invitations list --parent <accounts/{account}>`
- `google-business-profile-safe-cli account-management locations admins list --parent <locations/{location}>`
- `google-business-profile-safe-cli account-management locations admins create --parent <locations/{location}> --admin-file <path>`
- `google-business-profile-safe-cli account-management locations admins delete --name <locations/{location}/admins/{admin}>`
- `google-business-profile-safe-cli account-management locations admins patch --name <locations/{location}/admins/{admin}> --update-mask <field,...> --admin-file <path>`
- `google-business-profile-safe-cli account-management locations transfer --name <locations/{location}> --source-account <accounts/{account}> --destination-account <accounts/{account}>`
- `google-business-profile-safe-cli business-info accounts locations list --parent <accounts/{account}> --read-mask <mask>`
- `google-business-profile-safe-cli business-info accounts locations create --parent <accounts/{account}> --location-file <path-to-Location-JSON>`
- `google-business-profile-safe-cli business-info locations get --name <locations/{location}> --read-mask <mask>`
- `google-business-profile-safe-cli business-info locations get-attributes --name <locations/{location}/attributes>`
- `google-business-profile-safe-cli business-info locations get-google-updated --name <locations/{location}> --read-mask <mask>`
- `google-business-profile-safe-cli business-info locations attributes get-google-updated --name <locations/{location}/attributes>`
- `google-business-profile-safe-cli business-info attributes list --parent <locations/{location}>`
- `google-business-profile-safe-cli business-info attributes list --category-name <categories/{category_id}> --region-code <CC> --language-code <bcp47>`
- `google-business-profile-safe-cli business-info attributes list --show-all --region-code <CC> --language-code <bcp47>`
- `google-business-profile-safe-cli business-info categories list --region-code <CC> --language-code <bcp47> --view <BASIC|FULL>`
- `google-business-profile-safe-cli business-info categories batch-get --names <categories/{category_id}> --names <categories/{category_id}> [--names ...] --language-code <bcp47> --view <BASIC|FULL>`
- `google-business-profile-safe-cli business-info chains search --chain-name <name>`
- `google-business-profile-safe-cli business-info chains get --name <chains/{chain_place_id}>`
- `google-business-profile-safe-cli business-info google-locations search --query <text> | --location-file <path>`
- `google-business-profile-safe-cli business-info locations patch --name <locations/{location}> --update-mask <field,field,...> --location-file <path>`
- `google-business-profile-safe-cli business-info locations update-attributes --name <locations/{location}/attributes> --attribute-mask <attributes/{attribute},...> --attributes-file <path>`
- `google-business-profile-safe-cli business-info locations delete --name <locations/{location}>`
- `google-business-profile-safe-cli notifications accounts get-notification-setting --name <accounts/{account}/notificationSetting>`
- `google-business-profile-safe-cli notifications accounts update-notification-setting --name <accounts/{account}/notificationSetting> --notification-setting-file <path> --update-mask <field,field,...>`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews list --parent <accounts/{account}/locations/{location}> [--page-size ...] [--page-token ...] [--order-by ...]`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews get --name <accounts/{account}/locations/{location}/reviews/{review}>`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews update-reply --name <accounts/{account}/locations/{location}/reviews/{review}> --reply-file <path>`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews delete-reply --name <accounts/{account}/locations/{location}/reviews/{review}>`
- `google-business-profile-safe-cli legacy-v49 accounts locations verifications list --parent <accounts/{account}/locations/{location}> [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli legacy-v49 accounts locations verifications complete --name <accounts/{account}/locations/{location}/verifications/{verification}> --pin-file <path>`
- `google-business-profile-safe-cli legacy-v49 accounts locations transfer --name <accounts/{account}/locations/{location}> --to-account <accounts/{account}>`
- `google-business-profile-safe-cli media-upload-v1 media upload --resource-name <resource-name> --media-file <path-to-binary> | --media-json-file <path-to-Media-JSON> [--content-type <mime>]`
- `google-business-profile-safe-cli legacy-v49 accounts locations media start-upload --parent <accounts/{account}/locations/{location}>`
- `google-business-profile-safe-cli legacy-v49 accounts locations media create --parent <accounts/{account}/locations/{location}> --media-item-file <path-to-MediaItem-JSON>`
- `google-business-profile-safe-cli business-calls locations get-business-calls-settings --name <locations/{location}/businesscallssettings>`
- `google-business-profile-safe-cli business-calls locations update-business-calls-settings --name <locations/{location}/businesscallssettings> --update-mask <field,field,...> --business-calls-settings-file <path>`
- `google-business-profile-safe-cli business-calls locations business-calls-insights list --parent <locations/{location}> [--filter ...]`
- `google-business-profile-safe-cli place-actions locations place-action-links create --parent <locations/{location}> --place-action-link-file <path>`
- `google-business-profile-safe-cli place-actions locations place-action-links delete --name <locations/{location}/placeActionLinks/{id}>`
- `google-business-profile-safe-cli place-actions locations place-action-links get --name <locations/{location}/placeActionLinks/{id}>`
- `google-business-profile-safe-cli place-actions locations place-action-links list --parent <locations/{location}> [--filter ...] [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli place-actions locations place-action-links patch --name <locations/{location}/placeActionLinks/{id}> --update-mask <field,field,...> --place-action-link-file <path>`
- `google-business-profile-safe-cli place-actions place-action-type-metadata list --language-code <bcp47> --page-size ... --page-token ...`
- `google-business-profile-safe-cli lodging locations get-lodging --name <locations/{location}/lodging> --read-mask <mask>`
- `google-business-profile-safe-cli lodging locations update-lodging --name <locations/{location}/lodging> --update-mask <field,field,...> --lodging-file <path-to-Lodging-JSON>`
- `google-business-profile-safe-cli lodging locations lodging get-google-updated --name <locations/{location}/lodging> --read-mask <mask>`
- `google-business-profile-safe-cli performance locations fetch-multi-daily-metrics-time-series --location <locations/{location}> --daily-metrics <metric> [<metric> ...] --daily-range-start-year <YYYY> --daily-range-start-month <MM> --daily-range-start-day <DD> --daily-range-end-year <YYYY> --daily-range-end-month <MM> --daily-range-end-day <DD>`
- `google-business-profile-safe-cli performance locations get-daily-metrics-time-series --name <locations/{location}> --daily-metric <metric> --daily-range-start-year <YYYY> --daily-range-start-month <MM> --daily-range-start-day <DD> --daily-range-end-year <YYYY> --daily-range-end-month <MM> --daily-range-end-day <DD>`
- `google-business-profile-safe-cli performance locations search-keywords impressions monthly list --parent <locations/{location}> --monthly-range-start-year <YYYY> --monthly-range-start-month <MM> --monthly-range-end-year <YYYY> --monthly-range-end-month <MM>`
- `google-business-profile-safe-cli verifications locations fetch-verification-options --location <locations/{location}> --language-code <bcp47> --context-file <path-to-ServiceBusinessContext-JSON>`
- `google-business-profile-safe-cli verifications locations get-voice-of-merchant-state --name <locations/{location}>`
- `google-business-profile-safe-cli verifications locations verifications list --parent <locations/{location}> [--page-size ...] [--page-token ...]`
- `google-business-profile-safe-cli verifications locations verify --name <locations/{location}> --method <ADDRESS|EMAIL|PHONE_CALL|SMS|AUTO|TRUSTED_PARTNER> [--language-code ...] [--mailer-contact ...] [--phone-number ...] [--email-address ...] [--context-file <path-to-ServiceBusinessContext-JSON>] [--verification-token-file <path-to-VerificationToken-JSON>] [--trusted-partner-token-file <path>]`
- `google-business-profile-safe-cli verifications locations verifications complete --name <locations/{location}/verifications/{verification}> --pin-file <path>`

## Constraints

- Keep credentials local in `.state/oauth_credentials.json`.
- Never expose token values.
- Write commands are dry-run unless `--apply` is set.
- Current write apply attempts need `--ack-no-snapshot` before Google Business Profile HTTP when no before-state can be saved.
- For this write slice use `--plan-in` as a required safety check before apply when you use a saved plan, and save artifacts with `--plan-out`/`--receipt-out`.
- `account-management accounts create` and `account-management accounts patch` require matching `--plan-in` on apply.
- `account-management accounts admins create|delete|patch`, `account-management locations admins create|delete|patch`, `account-management locations transfer`, and `account-management accounts invitations accept|decline` require matching `--plan-in` on apply.
- `account-management accounts admins create|delete|patch` and `account-management locations admins create|delete|patch` also require `--yes` on apply.
- `account-management locations transfer` also requires `--yes`, `--ack-irreversible`, and different `--source-account` / `--destination-account` values on apply.
- `business-info locations delete` requires `--plan-in`, `--yes`, and `--ack-irreversible` on apply.
- `legacy-v49 accounts locations reviews update-reply` requires `--reply-file` with exactly `{"comment":"..."}` and matching `--plan-in` on apply.
- `legacy-v49 accounts locations reviews delete-reply` requires matching `--plan-in` and `--yes` on apply.
- `legacy-v49 accounts locations verifications complete` requires matching `--plan-in` on apply and uses `--pin-file` so the PIN is never passed directly on the command line.
- `legacy-v49 accounts locations transfer` requires `--plan-in`, `--yes`, and `--ack-irreversible` on apply, and `--to-account` must differ from the source account embedded in `--name`.
- `legacy-v49 accounts locations media start-upload` and `legacy-v49 accounts locations media create` are the focused legacy follow-up around the upload step; both require `--plan-in` on apply.
- `business-calls locations update-business-calls-settings` requires `--plan-in` on apply and uses read-back verification in `business-calls locations get-business-calls-settings`.
- `lodging locations update-lodging` requires `--plan-in` on apply and uses read-back verification in `lodging locations get-lodging`.
- `place-actions locations place-action-links create` and `place-actions locations place-action-links patch` require `--plan-in` on apply.
- `place-actions locations place-action-links delete` requires both `--plan-in` and `--yes` on apply.
- `verifications locations verify` and `verifications locations verifications complete` are write commands. Use file inputs for token-like values: `--verification-token-file`, `--trusted-partner-token-file`, and `--pin-file`.
- These write commands are dry-run unless `--apply` is set and require matching `--plan-in` for apply.
- Keep the command surface aligned to current implemented commands in `docs/api_coverage.md`.
- No generic endpoint builder or arbitrary URL execution is enabled.
- Prefer `--output json` for automation.
