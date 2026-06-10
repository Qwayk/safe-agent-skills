---
title: giftCardConfiguration - GraphQL Admin
description: The configuration for the shop's gift cards.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCardConfiguration
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCardConfiguration.md
---

# gift​Card​Configuration

query

The configuration for the shop's gift cards.

## Possible returns

* Gift​Card​Configuration

  [Gift​Card​Configuration!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardConfiguration)

  Represents information about the configuration of gift cards on the shop.

  * issue​Limit

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The issue limit for gift cards in the default shop currency.

  * purchase​Limit

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The purchase limit for gift cards in the default shop currency.

***

## Examples

* ### giftCardConfiguration reference
