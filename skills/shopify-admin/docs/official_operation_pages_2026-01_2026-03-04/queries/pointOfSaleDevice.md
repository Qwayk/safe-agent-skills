---
title: pointOfSaleDevice - GraphQL Admin
description: Returns a `PointOfSaleDevice` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/pointOfSaleDevice'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/pointOfSaleDevice.md
---

# point​Of​Sale​Device

query

Returns a `PointOfSaleDevice` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `PointOfSaleDevice` to return.

***

## Possible returns

* Point​Of​Sale​Device

  [Point​Of​Sale​Device](https://shopify.dev/docs/api/admin-graphql/latest/objects/PointOfSaleDevice)

  Represents a mobile device that Shopify Point of Sale has been installed on.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

***

## Examples

* ### pointOfSaleDevice reference
