---
title: pendingOrdersCount - GraphQL Admin
description: The number of pendings orders. Limited to a maximum of 10000.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/pendingOrdersCount'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/pendingOrdersCount.md
---

# pending​Orders​Count

query

Requires `read_orders` access scope.

The number of pendings orders. Limited to a maximum of 10000.

## Possible returns

* Count

  [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

  A numeric count with precision information indicating whether the count is exact or an estimate.

  * count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The count of elements.

  * precision

    [Count​Precision!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountPrecision)

    non-null

    The count's precision, or the exactness of the value.

***

## Examples

* ### pendingOrdersCount reference
