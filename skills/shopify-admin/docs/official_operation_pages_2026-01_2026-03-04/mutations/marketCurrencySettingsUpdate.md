---
title: marketCurrencySettingsUpdate - GraphQL Admin
description: Updates currency settings of a market.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketCurrencySettingsUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketCurrencySettingsUpdate.md
---

# market​Currency​Settings​Update

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Deprecated. This will be removed in a future version. Use [marketCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketCreate) and [marketUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketUpdate) for creating and updating market currency settings, respectively.

Updates currency settings of a market.

## Arguments

* input

  [Market​Currency​Settings​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketCurrencySettingsUpdateInput)

  required

  Properties to update for the market currency settings.

* market​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the market definition to target.

***

## Market​Currency​Settings​Update​Payload returns

* user​Errors

  [\[Market​Currency​Settings​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCurrencySettingsUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* market

  [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  Deprecated

  The market object.

***

## Examples

* ### marketCurrencySettingsUpdate reference
