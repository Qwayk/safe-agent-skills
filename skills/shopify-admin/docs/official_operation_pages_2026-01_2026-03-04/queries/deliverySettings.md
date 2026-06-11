---
title: deliverySettings - GraphQL Admin
description: Returns the shop-wide shipping settings.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/deliverySettings'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliverySettings.md
---

# delivery​Settings

query

Returns the shop-wide shipping settings.

## Possible returns

* Delivery​Setting

  [Delivery​Setting](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliverySetting)

  The `DeliverySetting` object enables you to manage shop-wide shipping settings.

  * legacy​Mode​Blocked

    [Delivery​Legacy​Mode​Blocked!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryLegacyModeBlocked)

    non-null

    Whether the shop is blocked from converting to full multi-location delivery profiles mode. If the shop is blocked, then the blocking reasons are also returned. Note: this field is effectively deprecated and will be removed in a future version of the API.

  * legacy​Mode​Profiles

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Enables legacy compatability mode for the multi-location delivery profiles feature. Note: this field is effectively deprecated and will be removed in a future version of the API.

***

## Examples

* ### deliverySettings reference
