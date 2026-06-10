---
title: metaobjectDefinitions - GraphQL Admin
description: >-
  Returns a paginated list of all
  [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)
  objects configured for the store. Metaobject definitions provide the schema
  for creating custom data structures composed of individual fields. Each
  definition specifies the field types, access permissions, and capabilities for
  [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)
  entries of that type. Use this query to discover available metaobject types
  before creating or querying metaobject entries.


  Learn more about [managing
  metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjectDefinitions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjectDefinitions.md
---

# metaobject​Definitions

query

Requires `read_metaobject_definitions` access scope.

Returns a paginated list of all [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition) objects configured for the store. Metaobject definitions provide the schema for creating custom data structures composed of individual fields. Each definition specifies the field types, access permissions, and capabilities for [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject) entries of that type. Use this query to discover available metaobject types before creating or querying metaobject entries.

Learn more about [managing metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).

## MetaobjectDefinitionConnection arguments

[MetaobjectDefinitionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetaobjectDefinitionConnection)

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

  [\[Metaobject​Definition​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinitionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Metaobject​Definition!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)

  non-null

  A list of nodes that are contained in MetaobjectDefinitionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### metaobjectDefinitions reference
