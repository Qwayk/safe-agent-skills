---
title: marketRegionsDelete - GraphQL Admin
description: Deletes a list of market regions.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketRegionsDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketRegionsDelete.md
---

# market​Regions​Delete

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Deprecated. Use [marketUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketUpdate) instead.

Deletes a list of market regions.

## Arguments

* ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A list of IDs of the market regions to delete.

***

## Market​Regions​Delete​Payload returns

* deleted​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted market region.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### marketRegionsDelete reference
