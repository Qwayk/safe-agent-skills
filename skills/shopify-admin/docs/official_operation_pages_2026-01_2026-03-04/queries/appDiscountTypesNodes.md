---
title: appDiscountTypesNodes - GraphQL Admin
description: A list of app discount types installed by apps.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/appDiscountTypesNodes
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/appDiscountTypesNodes.md
---

# app​Discount​Types​Nodes

query

A list of app discount types installed by apps.

## AppDiscountTypeConnection arguments

[AppDiscountTypeConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppDiscountTypeConnection)

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

  [\[App​Discount​Type​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppDiscountTypeEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[App​Discount​Type!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppDiscountType)

  non-null

  A list of nodes that are contained in AppDiscountTypeEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### appDiscountTypesNodes reference
