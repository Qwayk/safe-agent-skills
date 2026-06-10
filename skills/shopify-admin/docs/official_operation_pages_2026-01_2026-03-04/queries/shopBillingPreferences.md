---
title: shopBillingPreferences - GraphQL Admin
description: >-
  The shop's billing preferences, including the currency for paying for apps and
  services. Use this to create [app charges in the merchant's local billing
  currency](https://shopify.dev/docs/apps/launch/billing#supported-currencies),
  helping them budget their app spend without exposure to exchange rate
  fluctuations.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopBillingPreferences
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopBillingPreferences.md
---

# shop​Billing​Preferences

query

The shop's billing preferences, including the currency for paying for apps and services. Use this to create [app charges in the merchant's local billing currency](https://shopify.dev/docs/apps/launch/billing#supported-currencies), helping them budget their app spend without exposure to exchange rate fluctuations.

## Possible returns

* Shop​Billing​Preferences

  [Shop​Billing​Preferences!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopBillingPreferences)

  Billing preferences for the shop.

  * currency

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The currency the shop uses to pay for apps and services.

***

## Examples

* ### shopBillingPreferences reference
