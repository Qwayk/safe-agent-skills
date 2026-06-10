---
title: segmentFilterSuggestions - GraphQL Admin
description: >-
  A list of filter suggestions associated with a segment. A segment is a group
  of members (commonly customers) that meet specific criteria.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/segmentFilterSuggestions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/segmentFilterSuggestions.md
---

# segment​Filter​Suggestions

query

A list of filter suggestions associated with a segment. A segment is a group of members (commonly customers) that meet specific criteria.

## SegmentFilterConnection arguments

[SegmentFilterConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SegmentFilterConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  required

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* search

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  Returns the elements of a list by keyword or term.

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

* ### segmentFilterSuggestions reference
