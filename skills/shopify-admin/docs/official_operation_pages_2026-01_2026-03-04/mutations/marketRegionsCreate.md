---
title: marketRegionsCreate - GraphQL Admin
description: Creates regions that belong to an existing market.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketRegionsCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketRegionsCreate.md
---

# market​Regions​Create

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Deprecated. This mutation is deprecated and will be removed in the future. Use [marketCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketCreate) or [marketUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketUpdate) instead.

Creates regions that belong to an existing market.

## Arguments

* market​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the market to add the regions to.

* regions

  [\[Market​Region​Create​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketRegionCreateInput)

  required

  The regions to be created.

***

## Market​Regions​Create​Payload returns

* market

  [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  The market object.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### marketRegionsCreate reference
