---
title: segmentValueSuggestions - GraphQL Admin
description: >-
  The list of suggested values corresponding to a particular filter for a
  segment. A segment is a group of members, such as customers, that meet
  specific criteria.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/segmentValueSuggestions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/segmentValueSuggestions.md
---

# segment​Value​Suggestions

query

The list of suggested values corresponding to a particular filter for a segment. A segment is a group of members, such as customers, that meet specific criteria.

## SegmentValueConnection arguments

[SegmentValueConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SegmentValueConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* filter​Query​Name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Returns the elements of a list by filter handle.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* function​Parameter​Query​Name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Returns the elements of a list by filter parameter name.

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* search

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  Returns the elements of a list by keyword or term.

***

## Possible returns

* edges

  [\[Segment​Value​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentValueEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Segment​Value!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentValue)

  non-null

  A list of nodes that are contained in SegmentValueEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### segmentValueSuggestions reference
