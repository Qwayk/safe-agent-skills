---
title: catalogOperations - GraphQL Admin
description: Returns the most recent catalog operations for the shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogOperations'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogOperations.md
---

# catalog​Operations

query

Requires `read_products` access scope or `read_publications` access scope.

Returns the most recent catalog operations for the shop.

## Possible returns

* Resource​Operation

  [\[Resource​Operation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/ResourceOperation)

  Represents a merchandising background operation interface.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * processed​Row​Count

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The count of processed rows, summing imported, failed, and skipped rows.

  * row​Count

    [Row​Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/RowCount)

    Represents a rows objects within this background operation.

  * status

    [Resource​Operation​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ResourceOperationStatus)

    non-null

    The status of this operation.

***

## Examples

* ### catalogOperations reference
