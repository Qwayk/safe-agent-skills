---
title: publicationsCount - GraphQL Admin
description: Count of publications. Limited to a maximum of 10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/publicationsCount'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/publicationsCount.md
---

# publications​Count

query

Requires `read_publications` access scope.

Count of publications. Limited to a maximum of 10000 by default.

## Arguments

* catalog​Type

  [Catalog​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType)

  Filter publications by catalog type.

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The upper bound on count value before returning a result. Use `null` to have no limit.

***

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

* ### publicationsCount reference
