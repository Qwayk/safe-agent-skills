---
title: cartTransforms - GraphQL Admin
description: >-
  Retrieves all cart transform functions currently deployed by your app within
  the merchant's store. This query provides comprehensive access to your active
  cart modification logic, enabling management and monitoring of bundling and
  merchandising features.


  The query returns paginated results with full cart transform details,
  including function IDs, configuration settings, and operational status.


  Cart Transform ownership is scoped to your API client, ensuring you only see
  and manage functions deployed by your specific app. This isolation prevents
  conflicts between different apps while maintaining security boundaries for
  sensitive merchandising logic.


  Learn more about [managing cart
  transforms](https://shopify.dev/docs/api/functions/latest/cart-transform).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/cartTransforms'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/cartTransforms.md'
---

# cart​Transforms

query

Requires `read_cart_transforms` access scope.

Retrieves all cart transform functions currently deployed by your app within the merchant's store. This query provides comprehensive access to your active cart modification logic, enabling management and monitoring of bundling and merchandising features.

The query returns paginated results with full cart transform details, including function IDs, configuration settings, and operational status.

Cart Transform ownership is scoped to your API client, ensuring you only see and manage functions deployed by your specific app. This isolation prevents conflicts between different apps while maintaining security boundaries for sensitive merchandising logic.

Learn more about [managing cart transforms](https://shopify.dev/docs/api/functions/latest/cart-transform).

## CartTransformConnection arguments

[CartTransformConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CartTransformConnection)

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

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Cart​Transform​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CartTransformEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Cart​Transform!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CartTransform)

  non-null

  A list of nodes that are contained in CartTransformEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### cartTransforms reference
