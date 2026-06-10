---
title: marketsResolvedValues - GraphQL Admin
description: The resolved values for a buyer signal.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/marketsResolvedValues
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/marketsResolvedValues.md
---

# markets​Resolved​Values

query

The resolved values for a buyer signal.

## Arguments

* buyer​Signal

  [Buyer​Signal​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/BuyerSignalInput)

  required

  The buyer signal.

***

## Possible returns

* Markets​Resolved​Values

  [Markets​Resolved​Values!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketsResolvedValues)

  The resolved values based on the markets configuration for a buyer signal. Resolved values include the resolved catalogs, web presences, currency, and price inclusivity.

  * catalogs

    [Market​Catalog​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MarketCatalogConnection)

    non-null

    The resolved catalogs.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * currency​Code

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The resolved currency code.

  * price​Inclusivity

    [Resolved​Price​Inclusivity!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ResolvedPriceInclusivity)

    non-null

    The resolved price inclusivity attributes.

  * web​Presences

    [Market​Web​Presence​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MarketWebPresenceConnection)

    non-null

    The resolved web presences ordered by priority.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

***

## Examples

* ### marketsResolvedValues reference
