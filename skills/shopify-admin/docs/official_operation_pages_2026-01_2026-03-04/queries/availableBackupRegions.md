---
title: availableBackupRegions - GraphQL Admin
description: >-
  The geographic regions that you can set as the
  [`Shop`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)'s
  backup region. The backup region serves as a fallback when the system can't
  determine a buyer's actual location.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/availableBackupRegions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/availableBackupRegions.md
---

# available​Backup​Regions

query

The geographic regions that you can set as the [`Shop`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)'s backup region. The backup region serves as a fallback when the system can't determine a buyer's actual location.

## Possible returns

* Market​Region

  [\[Market​Region!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/MarketRegion)

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

* ### availableBackupRegions reference
