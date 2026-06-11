---
title: automaticDiscounts - GraphQL Admin
description: >-
  Returns a list of automatic discounts that are applied in the cart and at
  checkout without requiring a discount code.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscounts'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscounts.md
---

# automatic​Discounts

query

Deprecated. Use [automaticDiscountNodes](https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes) instead.

Returns a list of automatic discounts that are applied in the cart and at checkout without requiring a discount code.

## DiscountAutomaticConnection arguments

[DiscountAutomaticConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DiscountAutomaticConnection)

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

  * * default

      string

    * id

      id

    * status

      string

    * type

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the discount status.

    - Valid values:

      * `active`
      * `expired`
      * `scheduled`

      Example:

      * `status:scheduled`

      Filter by the [discount type](https://help.shopify.com/manual/discounts/discount-types).

      Valid values:

      * `all`
      * `all_with_app`
      * `app`
      * `bxgy`
      * `fixed_amount`
      * `percentage`

      Example:

      * `type:bxgy`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Automatic​Discount​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AutomaticDiscountSortKeys)

  Default:CREATED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Discount​Automatic​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Discount​Automatic!\]!](https://shopify.dev/docs/api/admin-graphql/latest/unions/DiscountAutomatic)

  non-null

  A list of nodes that are contained in DiscountAutomaticEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### automaticDiscounts reference
