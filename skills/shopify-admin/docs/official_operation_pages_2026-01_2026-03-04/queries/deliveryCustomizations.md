---
title: deliveryCustomizations - GraphQL Admin
description: The delivery customizations.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryCustomizations
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryCustomizations.md
---

# delivery​Customizations

query

Requires `read_delivery_customizations` access scope.

The delivery customizations.

## DeliveryCustomizationConnection arguments

[DeliveryCustomizationConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DeliveryCustomizationConnection)

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

  * enabled

    boolean

  * function\_id

    string

  * id

    id

    Filter by `id` range.

    Example:

    * `id:1234`
    * `id:>=1234`
    * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Delivery​Customization​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCustomizationEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Delivery​Customization!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCustomization)

  non-null

  A list of nodes that are contained in DeliveryCustomizationEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### deliveryCustomizations reference
