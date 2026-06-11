---
title: backupRegion - GraphQL Admin
description: The backup region of the shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/backupRegion'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/backupRegion.md'
---

# backup​Region

query

The backup region of the shop.

## Possible returns

* Market​Region

  [Market​Region!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/MarketRegion)

  A geographic region which comprises a market.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the region.

***

## Examples

* ### backupRegion reference
