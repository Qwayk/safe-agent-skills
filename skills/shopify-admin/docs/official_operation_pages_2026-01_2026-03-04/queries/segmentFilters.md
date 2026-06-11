---
title: segmentFilters - GraphQL Admin
description: A list of filters.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/segmentFilters'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/segmentFilters.md'
---

# segment​Filters

query

A list of filters.

## SegmentFilterConnection arguments

[SegmentFilterConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SegmentFilterConnection)

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

***

## Possible returns

* edges

  [\[Segment​Filter​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentFilterEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Segment​Filter!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/SegmentFilter)

  non-null

  A list of nodes that are contained in SegmentFilterEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### segmentFilters reference
