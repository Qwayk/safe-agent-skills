# Command reference

Use this page when you need the exact Google Merchant API command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--output json`: recommended for every automated call; the tool prints exactly one JSON object.
- `--apply`: required to execute any write. Without it, write commands stay in dry-run plan mode.
- `--yes`: required for higher-risk writes (`high` and `irreversible`).
- `--plan-out <file>`: save a dry-run plan for review.
- `--plan-in <file>`: required for `high` and `irreversible` apply calls; optional drift-check input for `medium` writes.
- `--receipt-out <file>`: reserved for future live receipts. Current write applies require explicit no-snapshot approval before provider HTTP because before-state capture is required but not supported yet.
- `--ack-irreversible`: extra confirmation required for `DELETE` applies.
- Global flags must be placed before the subcommand tree, for example: `google-merchant-api-tool --output json --apply accounts product-inputs insert ...`.

Current write behavior: dry-runs produce plans with `before_state.required: true` and `before_state.supported: false`. Apply attempts for writes require explicit no-snapshot approval before credentials or Google HTTP and say that no Google Merchant write was sent.

## Local utility commands

| Command | Purpose |
|---|---|
| `google-merchant-api-tool onboarding [--no-write-env]` | Create or explain local `.env` setup without printing secrets. |
| `google-merchant-api-tool auth check` | Validate configured auth mode and report safe status only. |
| `google-merchant-api-tool auth token set --file token.json` | Store an OAuth token file under local state. |
| `google-merchant-api-tool auth token status` | Show token-file status without printing token values. |
| `google-merchant-api-tool runs list [--limit 20]` | Show recent local run history rows. |
| `google-merchant-api-tool runs show --run-id <id>` | Show one local run summary and proof pointers. |

## Shipped Merchant command surface

- Total shipped Merchant operations: `224`
- Stable `v1` commands keep the short family path, for example `accounts list`.
- Non-`v1` commands insert the version token after the first family token, for example `accounts v1alpha loyalty-customers manage`.

### `accounts_v1` (76 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts autofeed-settings get-autofeed-settings` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts autofeed-settings update-autofeed-settings` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts automatic-improvements get-automatic-improvements` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts automatic-improvements update-automatic-improvements` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts business-identity get-business-identity` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts business-identity update-business-identity` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts business-info get-business-info` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts business-info update-business-info` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts create-and-configure` | `POST` | none | required | `medium` | `accounts/v1/accounts:createAndConfigure` |
| `google-merchant-api-tool accounts create-test-account` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}:createTestAccount` |
| `google-merchant-api-tool accounts delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts developer-registration get-account-for-gcp-registration` | `GET` | none | not used | `read` | `accounts/v1/accounts:getAccountForGcpRegistration` |
| `google-merchant-api-tool accounts developer-registration get-developer-registration` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts developer-registration register-gcp` | `POST` | `--name` | required | `medium` | `accounts/v1/{+name}:registerGcp` |
| `google-merchant-api-tool accounts developer-registration unregister-gcp` | `POST` | `--name` | required | `medium` | `accounts/v1/{+name}:unregisterGcp` |
| `google-merchant-api-tool accounts email-preferences get-email-preferences` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts email-preferences update-email-preferences` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts gbp-accounts link-gbp-account` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/gbpAccounts:linkGbpAccount` |
| `google-merchant-api-tool accounts gbp-accounts list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/gbpAccounts` |
| `google-merchant-api-tool accounts get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts homepage claim` | `POST` | `--name` | required | `medium` | `accounts/v1/{+name}:claim` |
| `google-merchant-api-tool accounts homepage get-homepage` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts homepage unclaim` | `POST` | `--name` | required | `medium` | `accounts/v1/{+name}:unclaim` |
| `google-merchant-api-tool accounts homepage update-homepage` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts issues list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/issues` |
| `google-merchant-api-tool accounts list` | `GET` | none | not used | `read` | `accounts/v1/accounts` |
| `google-merchant-api-tool accounts list-subaccounts` | `GET` | `--provider` | not used | `read` | `accounts/v1/{+provider}:listSubaccounts` |
| `google-merchant-api-tool accounts omnichannel-settings create` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/omnichannelSettings` |
| `google-merchant-api-tool accounts omnichannel-settings get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts omnichannel-settings lfp-providers find` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/lfpProviders:find` |
| `google-merchant-api-tool accounts omnichannel-settings lfp-providers link-lfp-provider` | `POST` | `--name` | required | `medium` | `accounts/v1/{+name}:linkLfpProvider` |
| `google-merchant-api-tool accounts omnichannel-settings list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/omnichannelSettings` |
| `google-merchant-api-tool accounts omnichannel-settings patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts omnichannel-settings request-inventory-verification` | `POST` | `--name` | required | `high` | `accounts/v1/{+name}:requestInventoryVerification` |
| `google-merchant-api-tool accounts online-return-policies create` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/onlineReturnPolicies` |
| `google-merchant-api-tool accounts online-return-policies delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts online-return-policies get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts online-return-policies list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/onlineReturnPolicies` |
| `google-merchant-api-tool accounts patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts programs checkout-settings create` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/checkoutSettings` |
| `google-merchant-api-tool accounts programs checkout-settings delete-checkout-settings` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts programs checkout-settings get-checkout-settings` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts programs checkout-settings update-checkout-settings` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts programs disable` | `POST` | `--name` | required | `high` | `accounts/v1/{+name}:disable` |
| `google-merchant-api-tool accounts programs enable` | `POST` | `--name` | required | `high` | `accounts/v1/{+name}:enable` |
| `google-merchant-api-tool accounts programs get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts programs list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/programs` |
| `google-merchant-api-tool accounts regions batch-create` | `POST` | `--parent` | required | `high` | `accounts/v1/{+parent}/regions:batchCreate` |
| `google-merchant-api-tool accounts regions batch-delete` | `POST` | `--parent` | required | `high` | `accounts/v1/{+parent}/regions:batchDelete` |
| `google-merchant-api-tool accounts regions batch-update` | `POST` | `--parent` | required | `high` | `accounts/v1/{+parent}/regions:batchUpdate` |
| `google-merchant-api-tool accounts regions create` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/regions` |
| `google-merchant-api-tool accounts regions delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts regions get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts regions list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/regions` |
| `google-merchant-api-tool accounts regions patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts relationships get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts relationships list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/relationships` |
| `google-merchant-api-tool accounts relationships patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts services approve` | `POST` | `--name` | required | `high` | `accounts/v1/{+name}:approve` |
| `google-merchant-api-tool accounts services get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts services list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/services` |
| `google-merchant-api-tool accounts services propose` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/services:propose` |
| `google-merchant-api-tool accounts services reject` | `POST` | `--name` | required | `high` | `accounts/v1/{+name}:reject` |
| `google-merchant-api-tool accounts shipping-settings get-shipping-settings` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts shipping-settings insert` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/shippingSettings:insert` |
| `google-merchant-api-tool accounts terms-of-service-agreement-states get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts terms-of-service-agreement-states retrieve-for-application` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/termsOfServiceAgreementStates:retrieveForApplication` |
| `google-merchant-api-tool accounts users create` | `POST` | `--parent` | required | `medium` | `accounts/v1/{+parent}/users` |
| `google-merchant-api-tool accounts users delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts users get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool accounts users list` | `GET` | `--parent` | not used | `read` | `accounts/v1/{+parent}/users` |
| `google-merchant-api-tool accounts users me verify-self` | `PATCH` | `--account` | required | `medium` | `accounts/v1/{+account}/users/me:verifySelf` |
| `google-merchant-api-tool accounts users patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1/{+name}` |
| `google-merchant-api-tool terms-of-service accept` | `POST` | `--name` | not used | `medium` | `accounts/v1/{+name}:accept` |
| `google-merchant-api-tool terms-of-service get` | `GET` | `--name` | not used | `read` | `accounts/v1/{+name}` |
| `google-merchant-api-tool terms-of-service retrieve-latest` | `GET` | none | not used | `read` | `accounts/v1/termsOfService:retrieveLatest` |

### `conversions_v1` (6 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts conversion-sources create` | `POST` | `--parent` | required | `medium` | `conversions/v1/{+parent}/conversionSources` |
| `google-merchant-api-tool accounts conversion-sources delete` | `DELETE` | `--name` | not used | `irreversible` | `conversions/v1/{+name}` |
| `google-merchant-api-tool accounts conversion-sources get` | `GET` | `--name` | not used | `read` | `conversions/v1/{+name}` |
| `google-merchant-api-tool accounts conversion-sources list` | `GET` | `--parent` | not used | `read` | `conversions/v1/{+parent}/conversionSources` |
| `google-merchant-api-tool accounts conversion-sources patch` | `PATCH` | `--name` | required | `medium` | `conversions/v1/{+name}` |
| `google-merchant-api-tool accounts conversion-sources undelete` | `POST` | `--name` | required | `medium` | `conversions/v1/{+name}:undelete` |

### `datasources_v1` (7 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts data-sources create` | `POST` | `--parent` | required | `medium` | `datasources/v1/{+parent}/dataSources` |
| `google-merchant-api-tool accounts data-sources delete` | `DELETE` | `--name` | not used | `irreversible` | `datasources/v1/{+name}` |
| `google-merchant-api-tool accounts data-sources fetch` | `POST` | `--name` | required | `medium` | `datasources/v1/{+name}:fetch` |
| `google-merchant-api-tool accounts data-sources file-uploads get` | `GET` | `--name` | not used | `read` | `datasources/v1/{+name}` |
| `google-merchant-api-tool accounts data-sources get` | `GET` | `--name` | not used | `read` | `datasources/v1/{+name}` |
| `google-merchant-api-tool accounts data-sources list` | `GET` | `--parent` | not used | `read` | `datasources/v1/{+parent}/dataSources` |
| `google-merchant-api-tool accounts data-sources patch` | `PATCH` | `--name` | required | `medium` | `datasources/v1/{+name}` |

### `inventories_v1` (6 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts products local-inventories delete` | `DELETE` | `--name` | not used | `irreversible` | `inventories/v1/{+name}` |
| `google-merchant-api-tool accounts products local-inventories insert` | `POST` | `--parent` | required | `medium` | `inventories/v1/{+parent}/localInventories:insert` |
| `google-merchant-api-tool accounts products local-inventories list` | `GET` | `--parent` | not used | `read` | `inventories/v1/{+parent}/localInventories` |
| `google-merchant-api-tool accounts products regional-inventories delete` | `DELETE` | `--name` | not used | `irreversible` | `inventories/v1/{+name}` |
| `google-merchant-api-tool accounts products regional-inventories insert` | `POST` | `--parent` | required | `medium` | `inventories/v1/{+parent}/regionalInventories:insert` |
| `google-merchant-api-tool accounts products regional-inventories list` | `GET` | `--parent` | not used | `read` | `inventories/v1/{+parent}/regionalInventories` |

### `issueresolution_v1` (4 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts aggregate-product-statuses list` | `GET` | `--parent` | not used | `read` | `issueresolution/v1/{+parent}/aggregateProductStatuses` |
| `google-merchant-api-tool issueresolution renderaccountissues` | `POST` | `--name` | required | `read` | `issueresolution/v1/{+name}:renderaccountissues` |
| `google-merchant-api-tool issueresolution renderproductissues` | `POST` | `--name` | required | `read` | `issueresolution/v1/{+name}:renderproductissues` |
| `google-merchant-api-tool issueresolution triggeraction` | `POST` | `--name` | required | `medium` | `issueresolution/v1/{+name}:triggeraction` |

### `lfp_v1` (7 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts lfp-inventories insert` | `POST` | `--parent` | required | `medium` | `lfp/v1/{+parent}/lfpInventories:insert` |
| `google-merchant-api-tool accounts lfp-merchant-states get` | `GET` | `--name` | not used | `read` | `lfp/v1/{+name}` |
| `google-merchant-api-tool accounts lfp-sales insert` | `POST` | `--parent` | required | `medium` | `lfp/v1/{+parent}/lfpSales:insert` |
| `google-merchant-api-tool accounts lfp-stores delete` | `DELETE` | `--name` | not used | `irreversible` | `lfp/v1/{+name}` |
| `google-merchant-api-tool accounts lfp-stores get` | `GET` | `--name` | not used | `read` | `lfp/v1/{+name}` |
| `google-merchant-api-tool accounts lfp-stores insert` | `POST` | `--parent` | required | `medium` | `lfp/v1/{+parent}/lfpStores:insert` |
| `google-merchant-api-tool accounts lfp-stores list` | `GET` | `--parent` | not used | `read` | `lfp/v1/{+parent}/lfpStores` |

### `notifications_v1` (5 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts notificationsubscriptions create` | `POST` | `--parent` | required | `medium` | `notifications/v1/{+parent}/notificationsubscriptions` |
| `google-merchant-api-tool accounts notificationsubscriptions delete` | `DELETE` | `--name` | not used | `irreversible` | `notifications/v1/{+name}` |
| `google-merchant-api-tool accounts notificationsubscriptions get` | `GET` | `--name` | not used | `read` | `notifications/v1/{+name}` |
| `google-merchant-api-tool accounts notificationsubscriptions list` | `GET` | `--parent` | not used | `read` | `notifications/v1/{+parent}/notificationsubscriptions` |
| `google-merchant-api-tool accounts notificationsubscriptions patch` | `PATCH` | `--name` | required | `medium` | `notifications/v1/{+name}` |

### `ordertracking_v1` (1 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts order-tracking-signals create` | `POST` | `--parent` | required | `medium` | `ordertracking/v1/{+parent}/orderTrackingSignals` |

### `products_v1` (5 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts product-inputs delete` | `DELETE` | `--name` | not used | `irreversible` | `products/v1/{+name}` |
| `google-merchant-api-tool accounts product-inputs insert` | `POST` | `--parent` | required | `medium` | `products/v1/{+parent}/productInputs:insert` |
| `google-merchant-api-tool accounts product-inputs patch` | `PATCH` | `--name` | required | `medium` | `products/v1/{+name}` |
| `google-merchant-api-tool accounts products get` | `GET` | `--name` | not used | `read` | `products/v1/{+name}` |
| `google-merchant-api-tool accounts products list` | `GET` | `--parent` | not used | `read` | `products/v1/{+parent}/products` |

### `promotions_v1` (3 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts promotions get` | `GET` | `--name` | not used | `read` | `promotions/v1/{+name}` |
| `google-merchant-api-tool accounts promotions insert` | `POST` | `--parent` | required | `medium` | `promotions/v1/{+parent}/promotions:insert` |
| `google-merchant-api-tool accounts promotions list` | `GET` | `--parent` | not used | `read` | `promotions/v1/{+parent}/promotions` |

### `quota_v1` (3 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts limits get` | `GET` | `--name` | not used | `read` | `quota/v1/{+name}` |
| `google-merchant-api-tool accounts limits list` | `GET` | `--parent` | not used | `read` | `quota/v1/{+parent}/limits` |
| `google-merchant-api-tool accounts quotas list` | `GET` | `--parent` | not used | `read` | `quota/v1/{+parent}/quotas` |

### `reports_v1` (1 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts reports search` | `POST` | `--parent` | required | `read` | `reports/v1/{+parent}/reports:search` |

### `accounts_v1alpha` (76 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha autofeed-settings get-autofeed-settings` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha autofeed-settings update-autofeed-settings` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha automatic-improvements get-automatic-improvements` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha automatic-improvements update-automatic-improvements` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha business-identity get-business-identity` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha business-identity update-business-identity` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha business-info get-business-info` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha business-info update-business-info` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha create-and-configure` | `POST` | none | required | `medium` | `accounts/v1alpha/accounts:createAndConfigure` |
| `google-merchant-api-tool accounts v1alpha create-test-account` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}:createTestAccount` |
| `google-merchant-api-tool accounts v1alpha delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha developer-registration get-account-for-gcp-registration` | `GET` | none | not used | `read` | `accounts/v1alpha/accounts:getAccountForGcpRegistration` |
| `google-merchant-api-tool accounts v1alpha developer-registration get-developer-registration` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha developer-registration register-gcp` | `POST` | `--name` | required | `medium` | `accounts/v1alpha/{+name}:registerGcp` |
| `google-merchant-api-tool accounts v1alpha developer-registration unregister-gcp` | `POST` | `--name` | required | `medium` | `accounts/v1alpha/{+name}:unregisterGcp` |
| `google-merchant-api-tool accounts v1alpha email-preferences get-email-preferences` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha email-preferences update-email-preferences` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha gbp-accounts link-gbp-account` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/gbpAccounts:linkGbpAccount` |
| `google-merchant-api-tool accounts v1alpha gbp-accounts list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/gbpAccounts` |
| `google-merchant-api-tool accounts v1alpha get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha homepage claim` | `POST` | `--name` | required | `medium` | `accounts/v1alpha/{+name}:claim` |
| `google-merchant-api-tool accounts v1alpha homepage get-homepage` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha homepage unclaim` | `POST` | `--name` | required | `medium` | `accounts/v1alpha/{+name}:unclaim` |
| `google-merchant-api-tool accounts v1alpha homepage update-homepage` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha issues list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/issues` |
| `google-merchant-api-tool accounts v1alpha list` | `GET` | none | not used | `read` | `accounts/v1alpha/accounts` |
| `google-merchant-api-tool accounts v1alpha list-subaccounts` | `GET` | `--provider` | not used | `read` | `accounts/v1alpha/{+provider}:listSubaccounts` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings create` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/omnichannelSettings` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings lfp-providers find` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/lfpProviders:find` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings lfp-providers link-lfp-provider` | `POST` | `--name` | required | `medium` | `accounts/v1alpha/{+name}:linkLfpProvider` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/omnichannelSettings` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha omnichannel-settings request-inventory-verification` | `POST` | `--name` | required | `high` | `accounts/v1alpha/{+name}:requestInventoryVerification` |
| `google-merchant-api-tool accounts v1alpha online-return-policies create` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/onlineReturnPolicies` |
| `google-merchant-api-tool accounts v1alpha online-return-policies delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha online-return-policies get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha online-return-policies list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/onlineReturnPolicies` |
| `google-merchant-api-tool accounts v1alpha patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha programs checkout-settings create` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/checkoutSettings` |
| `google-merchant-api-tool accounts v1alpha programs checkout-settings delete-checkout-settings` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha programs checkout-settings get-checkout-settings` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha programs checkout-settings update-checkout-settings` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha programs disable` | `POST` | `--name` | required | `high` | `accounts/v1alpha/{+name}:disable` |
| `google-merchant-api-tool accounts v1alpha programs enable` | `POST` | `--name` | required | `high` | `accounts/v1alpha/{+name}:enable` |
| `google-merchant-api-tool accounts v1alpha programs get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha programs list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/programs` |
| `google-merchant-api-tool accounts v1alpha regions batch-create` | `POST` | `--parent` | required | `high` | `accounts/v1alpha/{+parent}/regions:batchCreate` |
| `google-merchant-api-tool accounts v1alpha regions batch-delete` | `POST` | `--parent` | required | `high` | `accounts/v1alpha/{+parent}/regions:batchDelete` |
| `google-merchant-api-tool accounts v1alpha regions batch-update` | `POST` | `--parent` | required | `high` | `accounts/v1alpha/{+parent}/regions:batchUpdate` |
| `google-merchant-api-tool accounts v1alpha regions create` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/regions` |
| `google-merchant-api-tool accounts v1alpha regions delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha regions get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha regions list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/regions` |
| `google-merchant-api-tool accounts v1alpha regions patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha relationships get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha relationships list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/relationships` |
| `google-merchant-api-tool accounts v1alpha relationships patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha services approve` | `POST` | `--name` | required | `high` | `accounts/v1alpha/{+name}:approve` |
| `google-merchant-api-tool accounts v1alpha services get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha services list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/services` |
| `google-merchant-api-tool accounts v1alpha services propose` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/services:propose` |
| `google-merchant-api-tool accounts v1alpha services reject` | `POST` | `--name` | required | `high` | `accounts/v1alpha/{+name}:reject` |
| `google-merchant-api-tool accounts v1alpha shipping-settings get-shipping-settings` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha shipping-settings insert` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/shippingSettings:insert` |
| `google-merchant-api-tool accounts v1alpha terms-of-service-agreement-states get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha terms-of-service-agreement-states retrieve-for-application` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/termsOfServiceAgreementStates:retrieveForApplication` |
| `google-merchant-api-tool accounts v1alpha users create` | `POST` | `--parent` | required | `medium` | `accounts/v1alpha/{+parent}/users` |
| `google-merchant-api-tool accounts v1alpha users delete` | `DELETE` | `--name` | not used | `irreversible` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha users get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha users list` | `GET` | `--parent` | not used | `read` | `accounts/v1alpha/{+parent}/users` |
| `google-merchant-api-tool accounts v1alpha users me verify-self` | `PATCH` | `--account` | required | `medium` | `accounts/v1alpha/{+account}/users/me:verifySelf` |
| `google-merchant-api-tool accounts v1alpha users patch` | `PATCH` | `--name` | required | `medium` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool terms-of-service v1alpha accept` | `POST` | `--name` | not used | `medium` | `accounts/v1alpha/{+name}:accept` |
| `google-merchant-api-tool terms-of-service v1alpha get` | `GET` | `--name` | not used | `read` | `accounts/v1alpha/{+name}` |
| `google-merchant-api-tool terms-of-service v1alpha retrieve-latest` | `GET` | none | not used | `read` | `accounts/v1alpha/termsOfService:retrieveLatest` |

### `productstudio_v1alpha` (4 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha generated-images generate-product-image-background` | `POST` | `--name` | required | `medium` | `productstudio/v1alpha/{+name}/generatedImages:generateProductImageBackground` |
| `google-merchant-api-tool accounts v1alpha generated-images remove-product-image-background` | `POST` | `--name` | required | `medium` | `productstudio/v1alpha/{+name}/generatedImages:removeProductImageBackground` |
| `google-merchant-api-tool accounts v1alpha generated-images upscale-product-image` | `POST` | `--name` | required | `medium` | `productstudio/v1alpha/{+name}/generatedImages:upscaleProductImage` |
| `google-merchant-api-tool accounts v1alpha text-suggestions generate-product-text-suggestions` | `POST` | `--name` | required | `medium` | `productstudio/v1alpha/{+name}:generateProductTextSuggestions` |

### `reports_v1alpha` (1 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha reports search` | `POST` | `--parent` | required | `read` | `reports/v1alpha/{+parent}/reports:search` |

### `reviews_v1alpha` (8 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha merchant-reviews delete` | `DELETE` | `--name` | not used | `irreversible` | `reviews/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha merchant-reviews get` | `GET` | `--name` | not used | `read` | `reviews/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha merchant-reviews insert` | `POST` | `--parent` | required | `medium` | `reviews/v1alpha/{+parent}/merchantReviews:insert` |
| `google-merchant-api-tool accounts v1alpha merchant-reviews list` | `GET` | `--parent` | not used | `read` | `reviews/v1alpha/{+parent}/merchantReviews` |
| `google-merchant-api-tool accounts v1alpha product-reviews delete` | `DELETE` | `--name` | not used | `irreversible` | `reviews/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha product-reviews get` | `GET` | `--name` | not used | `read` | `reviews/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha product-reviews insert` | `POST` | `--parent` | required | `medium` | `reviews/v1alpha/{+parent}/productReviews:insert` |
| `google-merchant-api-tool accounts v1alpha product-reviews list` | `GET` | `--parent` | not used | `read` | `reviews/v1alpha/{+parent}/productReviews` |

### `youtube_v1alpha` (9 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha contracts commission-groups create` | `POST` | `--parent` | required | `medium` | `youtube/v1alpha/{+parent}/commissionGroups` |
| `google-merchant-api-tool accounts v1alpha contracts commission-groups delete` | `DELETE` | `--name` | not used | `irreversible` | `youtube/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha contracts commission-groups get` | `GET` | `--name` | not used | `read` | `youtube/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha contracts commission-groups list` | `GET` | `--parent` | not used | `read` | `youtube/v1alpha/{+parent}/commissionGroups` |
| `google-merchant-api-tool accounts v1alpha contracts commission-groups patch` | `PATCH` | `--name` | required | `medium` | `youtube/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha contracts create` | `POST` | `--parent` | required | `medium` | `youtube/v1alpha/{+parent}/contracts` |
| `google-merchant-api-tool accounts v1alpha contracts get` | `GET` | `--name` | not used | `read` | `youtube/v1alpha/{+name}` |
| `google-merchant-api-tool accounts v1alpha contracts list` | `GET` | `--parent` | not used | `read` | `youtube/v1alpha/{+parent}/contracts` |
| `google-merchant-api-tool accounts v1alpha contracts patch` | `PATCH` | `--name` | required | `medium` | `youtube/v1alpha/{+name}` |

### `loyaltycustomers_v1alpha` (1 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha loyalty-customers manage` | `POST` | `--parent` | required | `high` | `loyaltyCustomers/v1alpha/{parent=accounts/*}/loyaltyCustomers:manage` |

### `youtubeshoppingcheckout_v1alpha` (1 commands)

| Command | HTTP | Required path flags | Body | Risk | REST path |
|---|---|---|---|---|---|
| `google-merchant-api-tool accounts v1alpha orders apply-order-update` | `POST` | `--parent` | required | `high` | `youtubeshoppingcheckout/v1alpha/{parent=accounts/*/orders/*}:applyOrderUpdate` |
