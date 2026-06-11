---
title: catalogsCount - GraphQL Admin
description: >-
  The count of catalogs belonging to the shop. Limited to a maximum of 10000 by
  default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogsCount'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogsCount.md'
---

# catalogs​Count

query

The count of catalogs belonging to the shop. Limited to a maximum of 10000 by default.

## Arguments

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The upper bound on count value before returning a result. Use `null` to have no limit.

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * app\_id

      id

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * company\_id

    id

  * company\_location\_id

    id

  * * id

      id

    * managed\_country\_id

      id

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * market\_id

    id

  * status

    string

  * title

    string

* type

  [Catalog​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType)

  Default:null

  The type of the catalogs to be returned.

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

* ### catalogsCount reference
