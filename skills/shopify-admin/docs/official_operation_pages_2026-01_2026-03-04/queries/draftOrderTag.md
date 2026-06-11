---
title: draftOrderTag - GraphQL Admin
description: Returns a `DraftOrderTag` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrderTag'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrderTag.md'
---

# draft​Order​Tag

query

Returns a `DraftOrderTag` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `DraftOrderTag` to return.

***

## Possible returns

* Draft​Order​Tag

  [Draft​Order​Tag](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrderTag)

  Represents a draft order tag.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Handle of draft order tag.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    ID of draft order tag.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Title of draft order tag.

***

## Examples

* ### draftOrderTag reference
