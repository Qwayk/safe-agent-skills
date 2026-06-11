---
title: marketRegionDelete - GraphQL Admin
description: Deletes a market region.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketRegionDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketRegionDelete.md
---

# market​Region​Delete

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Deprecated. Use [marketUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketUpdate) instead.

Deletes a market region.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the market region to delete.

***

## Market​Region​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted market region.

* market

  [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  The parent market object of the deleted region.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### marketRegionDelete reference
