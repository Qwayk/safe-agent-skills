---
title: shopPayPaymentRequestReceipts - GraphQL Admin
description: Returns a list of Shop Pay payment request receipts.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopPayPaymentRequestReceipts
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopPayPaymentRequestReceipts.md
---

# shop​Pay​Payment​Request​Receipts

query

Returns a list of Shop Pay payment request receipts.

## ShopPayPaymentRequestReceiptConnection arguments

[ShopPayPaymentRequestReceiptConnection](https://shopify.dev/docs/api/admin-graphql/latest/connections/ShopPayPaymentRequestReceiptConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * created\_at

      time

    * id

      id

    * source\_identifier

      string

    * state

      string

    - Filter by the creation date of the payment request receipt.

    - Example:

      * `created_at:2021-01-01`
      * `created_at:2021-01-01..2021-01-02`
      * `created_at:<now`
      * `created_at:<2024-01-01`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the source identifier of the payment request receipt.

    - Example:

      * `source_identifier:1282823`

      Filter by the state of the payment request receipt. Options include: - COMPLETED - FAILED - PENDING - PROCESSING

      Example:

      * `state:COMPLETED`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Shop​Pay​Payment​Request​Receipts​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ShopPayPaymentRequestReceiptsSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Shop​Pay​Payment​Request​Receipt​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPayPaymentRequestReceiptEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Shop​Pay​Payment​Request​Receipt!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPayPaymentRequestReceipt)

  non-null

  A list of nodes that are contained in ShopPayPaymentRequestReceiptEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### shopPayPaymentRequestReceipts reference
